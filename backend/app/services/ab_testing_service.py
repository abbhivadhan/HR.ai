"""
A/B Testing Service for AI-HR Platform

Provides comprehensive A/B testing framework including:
- Test configuration and management
- Traffic splitting and variant assignment
- Statistical analysis and significance testing
- Results tracking and reporting
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import random
import hashlib
import statistics
try:
    from scipy import stats
    import numpy as np
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

from ..models.user import User


class ABTestStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ABTestingService:
    def __init__(self, db: Session):
        self.db = db

    def create_test(self, test_config: Dict[str, Any], creator_id: str) -> Dict[str, Any]:
        """Create a new A/B test"""
        test_id = f"ab_test_{int(datetime.utcnow().timestamp())}_{random.randint(1000, 9999)}"
        
        # Validate traffic splits sum to 100%
        total_traffic = sum(variant.get('traffic_split', 0) for variant in test_config['variants'])
        if abs(total_traffic - 100.0) > 0.01:
            raise ValueError("Traffic splits must sum to 100%")
        
        test = {
            "test_id": test_id,
            "test_name": test_config["test_name"],
            "description": test_config.get("description", ""),
            "creator_id": creator_id,
            "status": ABTestStatus.DRAFT,
            "created_at": datetime.utcnow(),
            "start_date": None,
            "end_date": None,
            "variants": test_config["variants"],
            "target_metric": test_config["target_metric"],
            "sample_size": test_config["sample_size"],
            "duration_days": test_config.get("duration_days", 14),
            "significance_level": test_config.get("significance_level", 0.95),
            "current_participants": 0,
            "results": None,
            "config": {
                "randomization_unit": test_config.get("randomization_unit", "user_id"),
                "minimum_sample_size": test_config.get("minimum_sample_size", 100),
                "early_stopping": test_config.get("early_stopping", True),
                "stratification": test_config.get("stratification", None)
            }
        }
        
        # In production, save to database
        # self._save_test_to_db(test)
        
        return test

    def start_test(self, test_id: str) -> Dict[str, Any]:
        """Start an A/B test"""
        test = self._get_test(test_id)
        
        if test["status"] != ABTestStatus.DRAFT:
            raise ValueError(f"Cannot start test in {test['status']} status")
        
        test["status"] = ABTestStatus.ACTIVE
        test["start_date"] = datetime.utcnow()
        
        # Calculate end date based on duration
        if test["duration_days"]:
            test["end_date"] = test["start_date"] + timedelta(days=test["duration_days"])
        
        # In production, update database
        # self._update_test_in_db(test)
        
        return test

    def stop_test(self, test_id: str, reason: str = "manual_stop") -> Dict[str, Any]:
        """Stop an A/B test"""
        test = self._get_test(test_id)
        
        if test["status"] != ABTestStatus.ACTIVE:
            raise ValueError(f"Cannot stop test in {test['status']} status")
        
        test["status"] = ABTestStatus.COMPLETED
        test["end_date"] = datetime.utcnow()
        test["stop_reason"] = reason
        
        # Generate final results
        test["results"] = self.calculate_test_results(test_id)
        
        # In production, update database
        # self._update_test_in_db(test)
        
        return test

    def assign_variant(self, test_id: str, user_id: str, 
                      context: Optional[Dict[str, Any]] = None) -> str:
        """Assign a user to a test variant"""
        test = self._get_test(test_id)
        
        if test["status"] != ABTestStatus.ACTIVE:
            return "control"  # Default to control if test not active
        
        # Check if user already assigned
        existing_assignment = self._get_user_assignment(test_id, user_id)
        if existing_assignment:
            return existing_assignment["variant"]
        
        # Determine variant based on consistent hashing
        variant = self._determine_variant(test, user_id, context)
        
        # Record assignment
        assignment = {
            "test_id": test_id,
            "user_id": user_id,
            "variant": variant,
            "assigned_at": datetime.utcnow(),
            "context": context or {}
        }
        
        # In production, save assignment to database
        # self._save_assignment_to_db(assignment)
        
        return variant

    def record_conversion(self, test_id: str, user_id: str, 
                         metric_value: float, event_data: Optional[Dict[str, Any]] = None):
        """Record a conversion event for A/B test"""
        test = self._get_test(test_id)
        assignment = self._get_user_assignment(test_id, user_id)
        
        if not assignment:
            return  # User not in test
        
        conversion = {
            "test_id": test_id,
            "user_id": user_id,
            "variant": assignment["variant"],
            "metric_value": metric_value,
            "converted_at": datetime.utcnow(),
            "event_data": event_data or {}
        }
        
        # In production, save conversion to database
        # self._save_conversion_to_db(conversion)

    def calculate_test_results(self, test_id: str) -> Dict[str, Any]:
        """Calculate comprehensive test results with statistical analysis"""
        test = self._get_test(test_id)
        
        # Get all assignments and conversions for this test
        assignments = self._get_test_assignments(test_id)
        conversions = self._get_test_conversions(test_id)
        
        if not assignments:
            return {"error": "No participants in test"}
        
        # Group data by variant
        variant_data = {}
        for variant in test["variants"]:
            variant_name = variant["name"]
            variant_assignments = [a for a in assignments if a["variant"] == variant_name]
            variant_conversions = [c for c in conversions if c["variant"] == variant_name]
            
            participants = len(variant_assignments)
            conversions_count = len(variant_conversions)
            conversion_rate = (conversions_count / participants) if participants > 0 else 0
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(
                conversions_count, participants, test["significance_level"]
            )
            
            # Calculate statistical power
            statistical_power = self._calculate_statistical_power(
                conversions_count, participants, conversion_rate
            )
            
            variant_data[variant_name] = {
                "name": variant_name,
                "participants": participants,
                "conversions": conversions_count,
                "conversion_rate": round(conversion_rate * 100, 2),
                "confidence_interval": confidence_interval,
                "statistical_power": statistical_power
            }
        
        # Perform statistical significance test
        significance_results = self._perform_significance_test(variant_data, test["significance_level"])
        
        # Generate insights and recommendations
        insights = self._generate_test_insights(variant_data, significance_results)
        recommendations = self._generate_test_recommendations(variant_data, significance_results)
        
        return {
            "test_id": test_id,
            "status": test["status"],
            "duration_days": self._calculate_test_duration(test),
            "total_participants": sum(v["participants"] for v in variant_data.values()),
            "variants": list(variant_data.values()),
            "statistical_significance": significance_results,
            "insights": insights,
            "recommendations": recommendations,
            "calculated_at": datetime.utcnow().isoformat()
        }

    def get_test_performance(self, test_id: str) -> Dict[str, Any]:
        """Get real-time test performance metrics"""
        test = self._get_test(test_id)
        results = self.calculate_test_results(test_id)
        
        if "error" in results:
            return results
        
        # Calculate additional performance metrics
        performance = {
            "test_id": test_id,
            "status": test["status"],
            "progress": self._calculate_test_progress(test),
            "sample_size_progress": {
                "current": results["total_participants"],
                "target": test["sample_size"],
                "percentage": min(100, (results["total_participants"] / test["sample_size"]) * 100)
            },
            "time_progress": self._calculate_time_progress(test),
            "early_stopping_recommendation": self._check_early_stopping(results, test),
            "estimated_completion": self._estimate_completion_date(test, results),
            "daily_metrics": self._get_daily_metrics(test_id)
        }
        
        return performance

    def list_tests(self, creator_id: Optional[str] = None, 
                  status: Optional[ABTestStatus] = None) -> List[Dict[str, Any]]:
        """List A/B tests with optional filtering"""
        # In production, query database with filters
        # Mock implementation
        tests = [
            {
                "test_id": "ab_test_1",
                "test_name": "Job Posting Layout Test",
                "status": "active",
                "created_at": datetime.utcnow() - timedelta(days=5),
                "start_date": datetime.utcnow() - timedelta(days=3),
                "participants": 847,
                "target_sample_size": 1000,
                "significance_level": 0.95
            },
            {
                "test_id": "ab_test_2",
                "test_name": "Application Form Optimization",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=20),
                "start_date": datetime.utcnow() - timedelta(days=18),
                "end_date": datetime.utcnow() - timedelta(days=4),
                "participants": 1250,
                "target_sample_size": 1200,
                "significance_level": 0.95
            }
        ]
        
        # Apply filters
        if creator_id:
            tests = [t for t in tests if t.get("creator_id") == creator_id]
        if status:
            tests = [t for t in tests if t["status"] == status]
        
        return tests

    # Helper methods
    def _get_test(self, test_id: str) -> Dict[str, Any]:
        """Get test configuration (mock implementation)"""
        # In production, query from database
        return {
            "test_id": test_id,
            "test_name": "Mock Test",
            "status": ABTestStatus.ACTIVE,
            "variants": [
                {"name": "control", "traffic_split": 50},
                {"name": "variant_a", "traffic_split": 50}
            ],
            "target_metric": "conversion_rate",
            "sample_size": 1000,
            "duration_days": 14,
            "significance_level": 0.95,
            "start_date": datetime.utcnow() - timedelta(days=7),
            "end_date": None
        }

    def _get_user_assignment(self, test_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's variant assignment (mock implementation)"""
        # In production, query from database
        return None

    def _get_test_assignments(self, test_id: str) -> List[Dict[str, Any]]:
        """Get all assignments for a test (mock implementation)"""
        # Mock data
        return [
            {"user_id": f"user_{i}", "variant": "control" if i % 2 == 0 else "variant_a"}
            for i in range(500)
        ]

    def _get_test_conversions(self, test_id: str) -> List[Dict[str, Any]]:
        """Get all conversions for a test (mock implementation)"""
        # Mock data - simulate conversions
        conversions = []
        for i in range(80):  # 80 conversions out of 500 participants
            variant = "control" if i % 3 == 0 else "variant_a"
            conversions.append({
                "user_id": f"user_{i}",
                "variant": variant,
                "metric_value": 1.0
            })
        return conversions

    def _determine_variant(self, test: Dict[str, Any], user_id: str, 
                          context: Optional[Dict[str, Any]]) -> str:
        """Determine variant assignment using consistent hashing"""
        # Create deterministic hash based on test_id and user_id
        hash_input = f"{test['test_id']}:{user_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # Convert to percentage (0-100)
        percentage = (hash_value % 10000) / 100.0
        
        # Assign based on traffic splits
        cumulative = 0
        for variant in test["variants"]:
            cumulative += variant["traffic_split"]
            if percentage < cumulative:
                return variant["name"]
        
        # Fallback to control
        return test["variants"][0]["name"]

    def _calculate_confidence_interval(self, conversions: int, participants: int, 
                                     confidence_level: float) -> List[float]:
        """Calculate confidence interval for conversion rate"""
        if participants == 0:
            return [0.0, 0.0]
        
        if not SCIPY_AVAILABLE:
            # Simple approximation without scipy
            conversion_rate = conversions / participants
            margin = 1.96 * (conversion_rate * (1 - conversion_rate) / participants) ** 0.5
            lower = max(0, conversion_rate - margin) * 100
            upper = min(1, conversion_rate + margin) * 100
            return [round(lower, 2), round(upper, 2)]
        
        conversion_rate = conversions / participants
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        # Wilson score interval
        n = participants
        p = conversion_rate
        
        denominator = 1 + z_score**2 / n
        centre_adjusted_probability = (p + z_score**2 / (2 * n)) / denominator
        adjusted_standard_deviation = np.sqrt((p * (1 - p) + z_score**2 / (4 * n)) / n) / denominator
        
        lower_bound = centre_adjusted_probability - z_score * adjusted_standard_deviation
        upper_bound = centre_adjusted_probability + z_score * adjusted_standard_deviation
        
        return [round(max(0, lower_bound) * 100, 2), round(min(1, upper_bound) * 100, 2)]

    def _calculate_statistical_power(self, conversions: int, participants: int, 
                                   conversion_rate: float) -> float:
        """Calculate statistical power of the test"""
        if participants == 0:
            return 0.0
        
        # Simplified power calculation
        # In production, use more sophisticated methods
        effect_size = 0.05  # Assume 5% minimum detectable effect
        alpha = 0.05
        
        # Mock calculation - in production, use proper statistical power analysis
        power = min(0.99, participants / 1000.0)  # Simple approximation
        
        return round(power, 3)

    def _perform_significance_test(self, variant_data: Dict[str, Any], 
                                 confidence_level: float) -> Dict[str, Any]:
        """Perform statistical significance test between variants"""
        variants = list(variant_data.values())
        
        if len(variants) < 2:
            return {"is_significant": False, "p_value": 1.0}
        
        # Compare first variant (control) with others
        control = variants[0]
        
        results = {
            "confidence_level": confidence_level,
            "comparisons": []
        }
        
        best_variant = control
        best_rate = control["conversion_rate"]
        
        for variant in variants[1:]:
            # Perform chi-square test
            control_conversions = int(control["conversions"])
            control_participants = control["participants"]
            variant_conversions = int(variant["conversions"])
            variant_participants = variant["participants"]
            
            if not SCIPY_AVAILABLE:
                # Simple z-test approximation
                control_rate = control_conversions / control_participants if control_participants > 0 else 0
                variant_rate = variant_conversions / variant_participants if variant_participants > 0 else 0
                
                # Simple significance test
                rate_diff = abs(variant_rate - control_rate)
                is_significant = rate_diff > 0.02  # 2% difference threshold
                p_value = 0.03 if is_significant else 0.15  # Mock p-values
                chi2 = 0.0
            else:
                # Create contingency table
                observed = np.array([
                    [control_conversions, control_participants - control_conversions],
                    [variant_conversions, variant_participants - variant_conversions]
                ])
                
                try:
                    chi2, p_value, _, _ = stats.chi2_contingency(observed)
                    is_significant = p_value < (1 - confidence_level)
                except ValueError:
                    # Handle cases with insufficient data
                    chi2, p_value, is_significant = 0.0, 1.0, False
                
            # Calculate improvement
            improvement = ((variant["conversion_rate"] - control["conversion_rate"]) / 
                         control["conversion_rate"] * 100) if control["conversion_rate"] > 0 else 0
            
            comparison = {
                "variant_name": variant["name"],
                "p_value": round(p_value, 4),
                "is_significant": is_significant,
                "improvement": round(improvement, 2),
                "chi2_statistic": round(chi2, 4)
            }
                
            results["comparisons"].append(comparison)
            
            # Track best performing variant
            if variant["conversion_rate"] > best_rate:
                best_variant = variant
                best_rate = variant["conversion_rate"]
                

        
        # Overall significance
        significant_comparisons = [c for c in results["comparisons"] if c["is_significant"]]
        results["is_significant"] = len(significant_comparisons) > 0
        results["winner"] = best_variant["name"] if results["is_significant"] else None
        results["overall_improvement"] = round(
            ((best_rate - control["conversion_rate"]) / control["conversion_rate"] * 100)
            if control["conversion_rate"] > 0 else 0, 2
        )
        
        return results

    def _generate_test_insights(self, variant_data: Dict[str, Any], 
                              significance_results: Dict[str, Any]) -> List[str]:
        """Generate insights from test results"""
        insights = []
        
        variants = list(variant_data.values())
        total_participants = sum(v["participants"] for v in variants)
        
        insights.append(f"Test completed with {total_participants} total participants")
        
        if significance_results["is_significant"]:
            winner = significance_results["winner"]
            improvement = significance_results["overall_improvement"]
            insights.append(f"Variant '{winner}' shows statistically significant improvement of {improvement}%")
        else:
            insights.append("No statistically significant difference detected between variants")
        
        # Check for sample size adequacy
        min_sample_per_variant = 100
        small_samples = [v for v in variants if v["participants"] < min_sample_per_variant]
        if small_samples:
            insights.append(f"Some variants have small sample sizes (< {min_sample_per_variant}), consider longer test duration")
        
        return insights

    def _generate_test_recommendations(self, variant_data: Dict[str, Any], 
                                     significance_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if significance_results["is_significant"]:
            winner = significance_results["winner"]
            recommendations.append(f"Implement variant '{winner}' as the new default")
            recommendations.append("Monitor performance for 2-4 weeks after implementation")
            recommendations.append("Consider testing additional variations to further optimize")
        else:
            recommendations.append("Continue with current implementation (control)")
            recommendations.append("Consider testing more dramatic variations")
            recommendations.append("Increase sample size or test duration for more statistical power")
        
        return recommendations

    def _calculate_test_duration(self, test: Dict[str, Any]) -> int:
        """Calculate test duration in days"""
        if not test.get("start_date"):
            return 0
        
        end_date = test.get("end_date", datetime.utcnow())
        return (end_date - test["start_date"]).days

    def _calculate_test_progress(self, test: Dict[str, Any]) -> Dict[str, float]:
        """Calculate test progress metrics"""
        if test["status"] != ABTestStatus.ACTIVE:
            return {"time": 100.0, "sample_size": 100.0}
        
        # Time progress
        if test.get("duration_days") and test.get("start_date"):
            elapsed_days = (datetime.utcnow() - test["start_date"]).days
            time_progress = min(100.0, (elapsed_days / test["duration_days"]) * 100)
        else:
            time_progress = 0.0
        
        # Sample size progress calculated elsewhere
        return {"time": round(time_progress, 1)}

    def _calculate_time_progress(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed time progress"""
        if not test.get("start_date"):
            return {"elapsed_days": 0, "remaining_days": 0, "percentage": 0}
        
        elapsed_days = (datetime.utcnow() - test["start_date"]).days
        
        if test.get("duration_days"):
            remaining_days = max(0, test["duration_days"] - elapsed_days)
            percentage = min(100, (elapsed_days / test["duration_days"]) * 100)
        else:
            remaining_days = None
            percentage = 0
        
        return {
            "elapsed_days": elapsed_days,
            "remaining_days": remaining_days,
            "percentage": round(percentage, 1)
        }

    def _check_early_stopping(self, results: Dict[str, Any], test: Dict[str, Any]) -> Dict[str, Any]:
        """Check if test should be stopped early"""
        if not test.get("config", {}).get("early_stopping", True):
            return {"recommended": False, "reason": "Early stopping disabled"}
        
        # Check for statistical significance with sufficient sample size
        if results.get("statistical_significance", {}).get("is_significant"):
            min_participants = test.get("config", {}).get("minimum_sample_size", 100)
            if results["total_participants"] >= min_participants:
                return {
                    "recommended": True,
                    "reason": "Statistical significance achieved with sufficient sample size"
                }
        
        return {"recommended": False, "reason": "Continue test as planned"}

    def _estimate_completion_date(self, test: Dict[str, Any], 
                                results: Dict[str, Any]) -> Optional[str]:
        """Estimate test completion date"""
        if test["status"] != ABTestStatus.ACTIVE:
            return None
        
        if test.get("end_date"):
            return test["end_date"].isoformat()
        
        # Estimate based on current participation rate
        if test.get("start_date") and results["total_participants"] > 0:
            elapsed_days = (datetime.utcnow() - test["start_date"]).days
            if elapsed_days > 0:
                daily_rate = results["total_participants"] / elapsed_days
                remaining_participants = test["sample_size"] - results["total_participants"]
                
                if daily_rate > 0 and remaining_participants > 0:
                    estimated_days = remaining_participants / daily_rate
                    completion_date = datetime.utcnow() + timedelta(days=estimated_days)
                    return completion_date.isoformat()
        
        return None

    def _get_daily_metrics(self, test_id: str) -> List[Dict[str, Any]]:
        """Get daily participation and conversion metrics"""
        # Mock implementation - in production, query database
        daily_metrics = []
        
        for i in range(7):  # Last 7 days
            date = datetime.utcnow() - timedelta(days=6-i)
            daily_metrics.append({
                "date": date.strftime("%Y-%m-%d"),
                "participants": random.randint(50, 150),
                "conversions": random.randint(5, 25),
                "conversion_rate": round(random.uniform(10, 20), 2)
            })
        
        return daily_metrics