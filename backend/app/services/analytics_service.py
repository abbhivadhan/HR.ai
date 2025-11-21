"""
Analytics Service for AI-HR Platform

This service provides comprehensive analytics and reporting capabilities including:
- Platform metrics and KPIs
- Hiring effectiveness tracking
- Candidate success insights
- Performance analytics
- A/B testing framework
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, case, extract, text
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics
from collections import defaultdict

from ..models.user import User, UserType
from ..models.profile import CandidateProfile, CompanyProfile
from ..models.job import JobPosting, JobApplication, ApplicationStatus, JobStatus
from ..models.assessment import Assessment, AssessmentStatus
from ..models.interview import Interview, InterviewStatus
from ..database import get_db


class MetricType(str, Enum):
    PLATFORM = "platform"
    HIRING = "hiring"
    CANDIDATE = "candidate"
    COMPANY = "company"
    ENGAGEMENT = "engagement"


class TimeRange(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    # Platform Metrics
    def get_platform_metrics(self, start_date: Optional[datetime] = None, 
                           end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive platform metrics"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()

        # User metrics
        total_users = self.db.query(User).count()
        candidates = self.db.query(User).filter(User.user_type == UserType.CANDIDATE).count()
        companies = self.db.query(User).filter(User.user_type == UserType.COMPANY).count()
        
        # Active users in period
        active_users = self.db.query(User).filter(
            and_(
                User.last_login >= start_date,
                User.last_login <= end_date
            )
        ).count()

        # Job metrics
        total_jobs = self.db.query(JobPosting).count()
        active_jobs = self.db.query(JobPosting).filter(
            JobPosting.status == JobStatus.ACTIVE
        ).count()
        
        jobs_in_period = self.db.query(JobPosting).filter(
            and_(
                JobPosting.created_at >= start_date,
                JobPosting.created_at <= end_date
            )
        ).count()

        # Application metrics
        total_applications = self.db.query(JobApplication).count()
        applications_in_period = self.db.query(JobApplication).filter(
            and_(
                JobApplication.applied_at >= start_date,
                JobApplication.applied_at <= end_date
            )
        ).count()

        # Assessment metrics
        total_assessments = self.db.query(Assessment).count()
        completed_assessments = self.db.query(Assessment).filter(
            Assessment.status == AssessmentStatus.COMPLETED
        ).count()

        # Interview metrics
        total_interviews = self.db.query(Interview).count()
        completed_interviews = self.db.query(Interview).filter(
            Interview.status == InterviewStatus.COMPLETED
        ).count()

        # Success rates
        application_success_rate = 0
        if total_applications > 0:
            successful_applications = self.db.query(JobApplication).filter(
                JobApplication.status == ApplicationStatus.ACCEPTED
            ).count()
            application_success_rate = (successful_applications / total_applications) * 100

        assessment_completion_rate = 0
        if total_assessments > 0:
            assessment_completion_rate = (completed_assessments / total_assessments) * 100

        return {
            "users": {
                "total": total_users,
                "candidates": candidates,
                "companies": companies,
                "active_in_period": active_users,
                "growth_rate": self._calculate_growth_rate("users", start_date, end_date)
            },
            "jobs": {
                "total": total_jobs,
                "active": active_jobs,
                "posted_in_period": jobs_in_period,
                "growth_rate": self._calculate_growth_rate("jobs", start_date, end_date)
            },
            "applications": {
                "total": total_applications,
                "in_period": applications_in_period,
                "success_rate": round(application_success_rate, 2),
                "growth_rate": self._calculate_growth_rate("applications", start_date, end_date)
            },
            "assessments": {
                "total": total_assessments,
                "completed": completed_assessments,
                "completion_rate": round(assessment_completion_rate, 2)
            },
            "interviews": {
                "total": total_interviews,
                "completed": completed_interviews
            }
        }

    def get_hiring_effectiveness_metrics(self, company_id: Optional[str] = None,
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get hiring effectiveness metrics for companies"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=90)
        if not end_date:
            end_date = datetime.utcnow()

        query = self.db.query(JobApplication).join(JobPosting)
        
        if company_id:
            query = query.filter(JobPosting.company_id == company_id)
        
        query = query.filter(
            and_(
                JobApplication.applied_at >= start_date,
                JobApplication.applied_at <= end_date
            )
        )

        applications = query.all()
        
        if not applications:
            return {
                "total_applications": 0,
                "hiring_rate": 0,
                "average_time_to_hire": 0,
                "cost_per_hire": 0,
                "quality_of_hire": 0,
                "source_effectiveness": {},
                "funnel_metrics": {}
            }

        # Calculate metrics
        total_applications = len(applications)
        hired_applications = [app for app in applications if app.status == ApplicationStatus.ACCEPTED]
        hiring_rate = (len(hired_applications) / total_applications) * 100

        # Average time to hire
        time_to_hire_days = []
        for app in hired_applications:
            if app.hired_at and app.applied_at:
                days = (app.hired_at - app.applied_at).days
                time_to_hire_days.append(days)
        
        avg_time_to_hire = statistics.mean(time_to_hire_days) if time_to_hire_days else 0

        # Funnel metrics
        funnel_metrics = self._calculate_hiring_funnel(applications)

        # Source effectiveness (mock data - would track actual sources)
        source_effectiveness = {
            "job_boards": {"applications": 45, "hires": 8, "rate": 17.8},
            "referrals": {"applications": 23, "hires": 7, "rate": 30.4},
            "social_media": {"applications": 32, "hires": 4, "rate": 12.5},
            "direct": {"applications": 18, "hires": 3, "rate": 16.7}
        }

        return {
            "total_applications": total_applications,
            "hiring_rate": round(hiring_rate, 2),
            "average_time_to_hire": round(avg_time_to_hire, 1),
            "cost_per_hire": 3500,  # Mock data
            "quality_of_hire": 4.2,  # Mock data
            "source_effectiveness": source_effectiveness,
            "funnel_metrics": funnel_metrics
        }

    def get_candidate_success_insights(self, candidate_id: Optional[str] = None) -> Dict[str, Any]:
        """Get candidate success tracking and insights"""
        query = self.db.query(User).filter(User.user_type == UserType.CANDIDATE)
        
        if candidate_id:
            query = query.filter(User.id == candidate_id)
        
        candidates = query.all()
        
        insights = {
            "total_candidates": len(candidates),
            "success_metrics": {},
            "skill_trends": {},
            "performance_distribution": {},
            "improvement_areas": []
        }

        if not candidates:
            return insights

        # Calculate success metrics
        all_applications = []
        all_assessments = []
        
        for candidate in candidates:
            applications = self.db.query(JobApplication).filter(
                JobApplication.candidate_id == candidate.id
            ).all()
            all_applications.extend(applications)
            
            assessments = self.db.query(Assessment).filter(
                and_(
                    Assessment.candidate_id == candidate.id,
                    Assessment.status == AssessmentStatus.COMPLETED
                )
            ).all()
            all_assessments.extend(assessments)

        # Success rates
        if all_applications:
            successful_apps = [app for app in all_applications if app.status == ApplicationStatus.ACCEPTED]
            success_rate = (len(successful_apps) / len(all_applications)) * 100
            
            insights["success_metrics"] = {
                "application_success_rate": round(success_rate, 2),
                "average_applications_per_candidate": len(all_applications) / len(candidates),
                "interview_conversion_rate": self._calculate_interview_conversion_rate(all_applications)
            }

        # Skill analysis
        if all_assessments:
            skill_scores = defaultdict(list)
            for assessment in all_assessments:
                if assessment.skill_scores:
                    scores = json.loads(assessment.skill_scores) if isinstance(assessment.skill_scores, str) else assessment.skill_scores
                    for skill, score in scores.items():
                        skill_scores[skill].append(score)
            
            skill_trends = {}
            for skill, scores in skill_scores.items():
                skill_trends[skill] = {
                    "average_score": round(statistics.mean(scores), 2),
                    "improvement_trend": self._calculate_skill_trend(skill, scores),
                    "candidate_count": len(scores)
                }
            
            insights["skill_trends"] = skill_trends

        return insights

    def get_performance_dashboard_data(self, company_id: str, 
                                     time_range: TimeRange = TimeRange.MONTHLY) -> Dict[str, Any]:
        """Get performance dashboard data for companies"""
        end_date = datetime.utcnow()
        
        if time_range == TimeRange.DAILY:
            start_date = end_date - timedelta(days=30)
            group_by = "day"
        elif time_range == TimeRange.WEEKLY:
            start_date = end_date - timedelta(weeks=12)
            group_by = "week"
        elif time_range == TimeRange.MONTHLY:
            start_date = end_date - timedelta(days=365)
            group_by = "month"
        else:
            start_date = end_date - timedelta(days=730)
            group_by = "quarter"

        # Job posting performance
        job_performance = self._get_job_posting_performance(company_id, start_date, end_date)
        
        # Application trends
        application_trends = self._get_application_trends(company_id, start_date, end_date, group_by)
        
        # Hiring metrics
        hiring_metrics = self.get_hiring_effectiveness_metrics(company_id, start_date, end_date)
        
        # Candidate quality metrics
        candidate_quality = self._get_candidate_quality_metrics(company_id, start_date, end_date)
        
        # ROI metrics
        roi_metrics = self._calculate_hiring_roi(company_id, start_date, end_date)

        return {
            "job_performance": job_performance,
            "application_trends": application_trends,
            "hiring_metrics": hiring_metrics,
            "candidate_quality": candidate_quality,
            "roi_metrics": roi_metrics,
            "time_range": time_range,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }

    def generate_automated_report(self, report_type: str, entity_id: Optional[str] = None,
                                time_range: TimeRange = TimeRange.MONTHLY) -> Dict[str, Any]:
        """Generate automated reports"""
        end_date = datetime.utcnow()
        start_date = self._get_start_date_for_range(end_date, time_range)
        
        report_data = {
            "report_id": f"{report_type}_{entity_id}_{int(datetime.utcnow().timestamp())}",
            "report_type": report_type,
            "generated_at": end_date.isoformat(),
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "range": time_range
            }
        }

        if report_type == "platform_overview":
            report_data["data"] = self.get_platform_metrics(start_date, end_date)
        elif report_type == "hiring_effectiveness" and entity_id:
            report_data["data"] = self.get_hiring_effectiveness_metrics(entity_id, start_date, end_date)
        elif report_type == "candidate_insights":
            report_data["data"] = self.get_candidate_success_insights(entity_id)
        elif report_type == "company_performance" and entity_id:
            report_data["data"] = self.get_performance_dashboard_data(entity_id, time_range)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

        # Add insights and recommendations
        report_data["insights"] = self._generate_insights(report_data["data"], report_type)
        report_data["recommendations"] = self._generate_recommendations(report_data["data"], report_type)

        return report_data

    # A/B Testing Framework
    def create_ab_test(self, test_name: str, variants: List[Dict[str, Any]], 
                      target_metric: str, sample_size: int) -> Dict[str, Any]:
        """Create A/B test configuration"""
        test_config = {
            "test_id": f"ab_test_{int(datetime.utcnow().timestamp())}",
            "test_name": test_name,
            "variants": variants,
            "target_metric": target_metric,
            "sample_size": sample_size,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "start_date": datetime.utcnow().isoformat(),
            "end_date": None,
            "results": None
        }
        
        # In production, store this in database
        return test_config

    def get_ab_test_results(self, test_id: str) -> Dict[str, Any]:
        """Get A/B test results and statistical significance"""
        # Mock implementation - in production, would analyze real test data
        results = {
            "test_id": test_id,
            "status": "completed",
            "duration_days": 14,
            "participants": 1250,
            "variants": [
                {
                    "name": "control",
                    "participants": 625,
                    "conversion_rate": 12.8,
                    "confidence_interval": [11.2, 14.4]
                },
                {
                    "name": "variant_a",
                    "participants": 625,
                    "conversion_rate": 15.2,
                    "confidence_interval": [13.5, 16.9]
                }
            ],
            "statistical_significance": {
                "p_value": 0.032,
                "confidence_level": 95,
                "is_significant": True,
                "winner": "variant_a",
                "improvement": 18.75
            },
            "recommendations": [
                "Implement variant_a as it shows significant improvement",
                "Monitor long-term effects for 30 days",
                "Consider testing additional variations"
            ]
        }
        
        return results

    # Helper methods
    def _calculate_growth_rate(self, metric_type: str, start_date: datetime, 
                             end_date: datetime) -> float:
        """Calculate growth rate for a metric"""
        period_length = (end_date - start_date).days
        previous_start = start_date - timedelta(days=period_length)
        
        if metric_type == "users":
            current_count = self.db.query(User).filter(
                and_(User.created_at >= start_date, User.created_at <= end_date)
            ).count()
            previous_count = self.db.query(User).filter(
                and_(User.created_at >= previous_start, User.created_at < start_date)
            ).count()
        elif metric_type == "jobs":
            current_count = self.db.query(JobPosting).filter(
                and_(JobPosting.created_at >= start_date, JobPosting.created_at <= end_date)
            ).count()
            previous_count = self.db.query(JobPosting).filter(
                and_(JobPosting.created_at >= previous_start, JobPosting.created_at < start_date)
            ).count()
        elif metric_type == "applications":
            current_count = self.db.query(JobApplication).filter(
                and_(JobApplication.applied_at >= start_date, JobApplication.applied_at <= end_date)
            ).count()
            previous_count = self.db.query(JobApplication).filter(
                and_(JobApplication.applied_at >= previous_start, JobApplication.applied_at < start_date)
            ).count()
        else:
            return 0.0
        
        if previous_count == 0:
            return 100.0 if current_count > 0 else 0.0
        
        return round(((current_count - previous_count) / previous_count) * 100, 2)

    def _calculate_hiring_funnel(self, applications: List[JobApplication]) -> Dict[str, Any]:
        """Calculate hiring funnel metrics"""
        total = len(applications)
        if total == 0:
            return {}
        
        pending = len([app for app in applications if app.status == ApplicationStatus.PENDING])
        reviewing = len([app for app in applications if app.status == ApplicationStatus.REVIEWING])
        shortlisted = len([app for app in applications if app.status == ApplicationStatus.SHORTLISTED])
        interviewed = len([app for app in applications if app.status == ApplicationStatus.INTERVIEWED])
        accepted = len([app for app in applications if app.status == ApplicationStatus.ACCEPTED])
        rejected = len([app for app in applications if app.status == ApplicationStatus.REJECTED])
        
        return {
            "applied": {"count": total, "percentage": 100.0},
            "reviewing": {"count": reviewing, "percentage": round((reviewing / total) * 100, 2)},
            "shortlisted": {"count": shortlisted, "percentage": round((shortlisted / total) * 100, 2)},
            "interviewed": {"count": interviewed, "percentage": round((interviewed / total) * 100, 2)},
            "accepted": {"count": accepted, "percentage": round((accepted / total) * 100, 2)},
            "rejected": {"count": rejected, "percentage": round((rejected / total) * 100, 2)}
        }

    def _calculate_interview_conversion_rate(self, applications: List[JobApplication]) -> float:
        """Calculate interview conversion rate"""
        total_apps = len(applications)
        if total_apps == 0:
            return 0.0
        
        interviewed = len([app for app in applications 
                         if app.status in [ApplicationStatus.INTERVIEWED, ApplicationStatus.ACCEPTED]])
        
        return round((interviewed / total_apps) * 100, 2)

    def _calculate_skill_trend(self, skill: str, scores: List[float]) -> str:
        """Calculate skill improvement trend"""
        if len(scores) < 2:
            return "insufficient_data"
        
        # Simple trend calculation - in production, use more sophisticated analysis
        recent_avg = statistics.mean(scores[-3:]) if len(scores) >= 3 else scores[-1]
        older_avg = statistics.mean(scores[:-3]) if len(scores) >= 6 else statistics.mean(scores[:-1])
        
        if recent_avg > older_avg * 1.05:
            return "improving"
        elif recent_avg < older_avg * 0.95:
            return "declining"
        else:
            return "stable"

    def _get_job_posting_performance(self, company_id: str, start_date: datetime, 
                                   end_date: datetime) -> Dict[str, Any]:
        """Get job posting performance metrics"""
        jobs = self.db.query(JobPosting).filter(
            and_(
                JobPosting.company_id == company_id,
                JobPosting.created_at >= start_date,
                JobPosting.created_at <= end_date
            )
        ).all()
        
        if not jobs:
            return {"total_jobs": 0, "performance": []}
        
        performance = []
        for job in jobs:
            applications_count = self.db.query(JobApplication).filter(
                JobApplication.job_posting_id == job.id
            ).count()
            
            performance.append({
                "job_id": str(job.id),
                "title": job.title,
                "applications": applications_count,
                "views": job.view_count or 0,
                "application_rate": round((applications_count / max(job.view_count, 1)) * 100, 2),
                "status": job.status
            })
        
        return {
            "total_jobs": len(jobs),
            "performance": performance
        }

    def _get_application_trends(self, company_id: str, start_date: datetime, 
                              end_date: datetime, group_by: str) -> List[Dict[str, Any]]:
        """Get application trends over time"""
        # This would use more sophisticated SQL grouping in production
        applications = self.db.query(JobApplication).join(JobPosting).filter(
            and_(
                JobPosting.company_id == company_id,
                JobApplication.applied_at >= start_date,
                JobApplication.applied_at <= end_date
            )
        ).all()
        
        # Group by time period
        trends = defaultdict(int)
        for app in applications:
            if group_by == "day":
                key = app.applied_at.strftime("%Y-%m-%d")
            elif group_by == "week":
                key = app.applied_at.strftime("%Y-W%U")
            elif group_by == "month":
                key = app.applied_at.strftime("%Y-%m")
            else:
                key = f"{app.applied_at.year}-Q{(app.applied_at.month-1)//3 + 1}"
            
            trends[key] += 1
        
        return [{"period": period, "applications": count} for period, count in sorted(trends.items())]

    def _get_candidate_quality_metrics(self, company_id: str, start_date: datetime, 
                                     end_date: datetime) -> Dict[str, Any]:
        """Get candidate quality metrics"""
        applications = self.db.query(JobApplication).join(JobPosting).filter(
            and_(
                JobPosting.company_id == company_id,
                JobApplication.applied_at >= start_date,
                JobApplication.applied_at <= end_date
            )
        ).all()
        
        if not applications:
            return {"average_score": 0, "score_distribution": {}}
        
        # Get assessment scores for candidates
        candidate_ids = [app.candidate_id for app in applications]
        assessments = self.db.query(Assessment).filter(
            and_(
                Assessment.candidate_id.in_(candidate_ids),
                Assessment.status == AssessmentStatus.COMPLETED
            )
        ).all()
        
        scores = [ass.percentage_score for ass in assessments if ass.percentage_score]
        
        if not scores:
            return {"average_score": 0, "score_distribution": {}}
        
        avg_score = statistics.mean(scores)
        
        # Score distribution
        distribution = {
            "0-20": len([s for s in scores if 0 <= s < 20]),
            "20-40": len([s for s in scores if 20 <= s < 40]),
            "40-60": len([s for s in scores if 40 <= s < 60]),
            "60-80": len([s for s in scores if 60 <= s < 80]),
            "80-100": len([s for s in scores if 80 <= s <= 100])
        }
        
        return {
            "average_score": round(avg_score, 2),
            "score_distribution": distribution,
            "total_assessed": len(scores)
        }

    def _calculate_hiring_roi(self, company_id: str, start_date: datetime, 
                            end_date: datetime) -> Dict[str, Any]:
        """Calculate hiring ROI metrics"""
        # Mock implementation - in production, would use actual cost data
        hired_count = self.db.query(JobApplication).join(JobPosting).filter(
            and_(
                JobPosting.company_id == company_id,
                JobApplication.status == ApplicationStatus.ACCEPTED,
                JobApplication.hired_at >= start_date,
                JobApplication.hired_at <= end_date
            )
        ).count()
        
        # Mock costs and benefits
        cost_per_hire = 3500
        total_hiring_cost = hired_count * cost_per_hire
        average_salary = 75000
        productivity_gain = 0.15  # 15% productivity improvement
        
        annual_benefit = hired_count * average_salary * productivity_gain
        roi_percentage = ((annual_benefit - total_hiring_cost) / total_hiring_cost) * 100 if total_hiring_cost > 0 else 0
        
        return {
            "total_hires": hired_count,
            "cost_per_hire": cost_per_hire,
            "total_cost": total_hiring_cost,
            "annual_benefit": annual_benefit,
            "roi_percentage": round(roi_percentage, 2),
            "payback_period_months": round((total_hiring_cost / (annual_benefit / 12)), 1) if annual_benefit > 0 else 0
        }

    def _get_start_date_for_range(self, end_date: datetime, time_range: TimeRange) -> datetime:
        """Get start date for time range"""
        if time_range == TimeRange.DAILY:
            return end_date - timedelta(days=30)
        elif time_range == TimeRange.WEEKLY:
            return end_date - timedelta(weeks=12)
        elif time_range == TimeRange.MONTHLY:
            return end_date - timedelta(days=365)
        elif time_range == TimeRange.QUARTERLY:
            return end_date - timedelta(days=730)
        else:
            return end_date - timedelta(days=365)

    def _generate_insights(self, data: Dict[str, Any], report_type: str) -> List[str]:
        """Generate insights from report data"""
        insights = []
        
        if report_type == "platform_overview":
            if data.get("users", {}).get("growth_rate", 0) > 10:
                insights.append("Strong user growth indicates healthy platform adoption")
            if data.get("applications", {}).get("success_rate", 0) > 15:
                insights.append("Above-average application success rate shows good job-candidate matching")
        
        elif report_type == "hiring_effectiveness":
            if data.get("hiring_rate", 0) > 20:
                insights.append("High hiring rate indicates effective screening process")
            if data.get("average_time_to_hire", 0) < 21:
                insights.append("Fast hiring process gives competitive advantage")
        
        return insights

    def _generate_recommendations(self, data: Dict[str, Any], report_type: str) -> List[str]:
        """Generate recommendations from report data"""
        recommendations = []
        
        if report_type == "platform_overview":
            if data.get("assessments", {}).get("completion_rate", 0) < 70:
                recommendations.append("Consider simplifying assessment process to improve completion rates")
        
        elif report_type == "hiring_effectiveness":
            if data.get("average_time_to_hire", 0) > 30:
                recommendations.append("Streamline interview process to reduce time to hire")
        
        return recommendations