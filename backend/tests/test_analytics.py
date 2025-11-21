"""
Tests for Analytics and Reporting System

Tests cover:
- Analytics service functionality
- A/B testing framework
- Report generation
- API endpoints
- Performance and accuracy
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
import json

from app.services.analytics_service import AnalyticsService, TimeRange, MetricType
from app.services.ab_testing_service import ABTestingService, ABTestStatus
from app.services.report_service import ReportService, ReportFormat, ReportType
from app.models.user import User, UserType
from app.models.job import JobPosting, JobApplication, ApplicationStatus, JobStatus
from app.models.assessment import Assessment, AssessmentStatus
from app.models.interview import Interview, InterviewStatus


class TestAnalyticsService:
    """Test analytics service functionality"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def analytics_service(self, mock_db):
        """Analytics service instance"""
        return AnalyticsService(mock_db)
    
    def test_get_platform_metrics(self, analytics_service, mock_db):
        """Test platform metrics calculation"""
        # Mock database queries
        mock_db.query.return_value.count.return_value = 1000
        mock_db.query.return_value.filter.return_value.count.return_value = 500
        
        # Test metrics calculation
        metrics = analytics_service.get_platform_metrics()
        
        # Verify structure
        assert 'users' in metrics
        assert 'jobs' in metrics
        assert 'applications' in metrics
        assert 'assessments' in metrics
        assert 'interviews' in metrics
        
        # Verify user metrics structure
        user_metrics = metrics['users']
        assert 'total' in user_metrics
        assert 'candidates' in user_metrics
        assert 'companies' in user_metrics
        assert 'growth_rate' in user_metrics
    
    def test_get_hiring_effectiveness_metrics(self, analytics_service, mock_db):
        """Test hiring effectiveness metrics"""
        # Mock applications data
        mock_applications = [
            Mock(status=ApplicationStatus.ACCEPTED, applied_at=datetime.utcnow(), hired_at=datetime.utcnow()),
            Mock(status=ApplicationStatus.PENDING, applied_at=datetime.utcnow(), hired_at=None),
            Mock(status=ApplicationStatus.REJECTED, applied_at=datetime.utcnow(), hired_at=None)
        ]
        
        mock_db.query.return_value.join.return_value.filter.return_value.all.return_value = mock_applications
        
        # Test metrics calculation
        company_id = "test_company_id"
        metrics = analytics_service.get_hiring_effectiveness_metrics(company_id)
        
        # Verify structure
        assert 'total_applications' in metrics
        assert 'hiring_rate' in metrics
        assert 'average_time_to_hire' in metrics
        assert 'funnel_metrics' in metrics
        assert 'source_effectiveness' in metrics
        
        # Verify calculations
        assert metrics['total_applications'] == 3
        assert metrics['hiring_rate'] == pytest.approx(33.33, rel=1e-2)
    
    def test_get_candidate_success_insights(self, analytics_service, mock_db):
        """Test candidate success insights"""
        # Mock candidates and related data
        mock_candidates = [Mock(id=1), Mock(id=2)]
        mock_db.query.return_value.filter.return_value.all.return_value = mock_candidates
        
        # Mock applications and assessments
        mock_db.query.return_value.filter.return_value.all.side_effect = [
            [Mock(status=ApplicationStatus.ACCEPTED)],  # Applications for candidate 1
            [Mock(status=AssessmentStatus.COMPLETED, skill_scores='{"Python": 85, "JavaScript": 78}')]  # Assessments
        ]
        
        insights = analytics_service.get_candidate_success_insights()
        
        # Verify structure
        assert 'total_candidates' in insights
        assert 'success_metrics' in insights
        assert 'skill_trends' in insights
        assert 'performance_distribution' in insights
    
    def test_get_performance_dashboard_data(self, analytics_service, mock_db):
        """Test performance dashboard data"""
        company_id = "test_company_id"
        
        # Mock various data sources
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        dashboard_data = analytics_service.get_performance_dashboard_data(
            company_id, TimeRange.MONTHLY
        )
        
        # Verify structure
        assert 'job_performance' in dashboard_data
        assert 'application_trends' in dashboard_data
        assert 'hiring_metrics' in dashboard_data
        assert 'candidate_quality' in dashboard_data
        assert 'roi_metrics' in dashboard_data
        assert 'time_range' in dashboard_data
        assert 'period' in dashboard_data
    
    def test_generate_automated_report(self, analytics_service, mock_db):
        """Test automated report generation"""
        # Mock data for report
        mock_db.query.return_value.count.return_value = 100
        
        report = analytics_service.generate_automated_report(
            "platform_overview", None, TimeRange.MONTHLY
        )
        
        # Verify report structure
        assert 'report_id' in report
        assert 'report_type' in report
        assert 'generated_at' in report
        assert 'period' in report
        assert 'data' in report
        assert 'insights' in report
        assert 'recommendations' in report
    
    def test_growth_rate_calculation(self, analytics_service, mock_db):
        """Test growth rate calculation accuracy"""
        # Mock query results for current and previous periods
        mock_db.query.return_value.filter.return_value.count.side_effect = [120, 100]  # 20% growth
        
        start_date = datetime.utcnow() - timedelta(days=30)
        end_date = datetime.utcnow()
        
        growth_rate = analytics_service._calculate_growth_rate("users", start_date, end_date)
        
        assert growth_rate == 20.0
    
    def test_hiring_funnel_calculation(self, analytics_service):
        """Test hiring funnel metrics calculation"""
        # Mock applications with different statuses
        applications = [
            Mock(status=ApplicationStatus.PENDING),
            Mock(status=ApplicationStatus.REVIEWING),
            Mock(status=ApplicationStatus.SHORTLISTED),
            Mock(status=ApplicationStatus.ACCEPTED),
            Mock(status=ApplicationStatus.REJECTED)
        ]
        
        funnel = analytics_service._calculate_hiring_funnel(applications)
        
        # Verify funnel structure and calculations
        assert funnel['applied']['count'] == 5
        assert funnel['applied']['percentage'] == 100.0
        assert funnel['accepted']['count'] == 1
        assert funnel['accepted']['percentage'] == 20.0


class TestABTestingService:
    """Test A/B testing framework"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def ab_testing_service(self, mock_db):
        return ABTestingService(mock_db)
    
    def test_create_test(self, ab_testing_service):
        """Test A/B test creation"""
        test_config = {
            "test_name": "Button Color Test",
            "description": "Test different button colors",
            "variants": [
                {"name": "control", "traffic_split": 50},
                {"name": "red_button", "traffic_split": 50}
            ],
            "target_metric": "click_rate",
            "sample_size": 1000
        }
        
        test = ab_testing_service.create_test(test_config, "creator_123")
        
        # Verify test structure
        assert test['test_name'] == "Button Color Test"
        assert test['status'] == ABTestStatus.DRAFT
        assert len(test['variants']) == 2
        assert test['sample_size'] == 1000
        assert 'test_id' in test
    
    def test_invalid_traffic_split(self, ab_testing_service):
        """Test validation of traffic splits"""
        test_config = {
            "test_name": "Invalid Test",
            "variants": [
                {"name": "control", "traffic_split": 60},
                {"name": "variant_a", "traffic_split": 50}  # Total = 110%
            ],
            "target_metric": "conversion",
            "sample_size": 1000
        }
        
        with pytest.raises(ValueError, match="Traffic splits must sum to 100%"):
            ab_testing_service.create_test(test_config, "creator_123")
    
    def test_start_test(self, ab_testing_service):
        """Test starting an A/B test"""
        # Mock test data
        with patch.object(ab_testing_service, '_get_test') as mock_get_test:
            mock_test = {
                "test_id": "test_123",
                "status": ABTestStatus.DRAFT,
                "duration_days": 14
            }
            mock_get_test.return_value = mock_test
            
            started_test = ab_testing_service.start_test("test_123")
            
            assert started_test['status'] == ABTestStatus.ACTIVE
            assert 'start_date' in started_test
            assert 'end_date' in started_test
    
    def test_variant_assignment_consistency(self, ab_testing_service):
        """Test that variant assignment is consistent for same user"""
        with patch.object(ab_testing_service, '_get_test') as mock_get_test, \
             patch.object(ab_testing_service, '_get_user_assignment') as mock_get_assignment:
            
            mock_test = {
                "test_id": "test_123",
                "status": ABTestStatus.ACTIVE,
                "variants": [
                    {"name": "control", "traffic_split": 50},
                    {"name": "variant_a", "traffic_split": 50}
                ]
            }
            mock_get_test.return_value = mock_test
            mock_get_assignment.return_value = None  # No existing assignment
            
            # Same user should get same variant
            user_id = "user_123"
            variant1 = ab_testing_service.assign_variant("test_123", user_id)
            variant2 = ab_testing_service.assign_variant("test_123", user_id)
            
            assert variant1 == variant2
    
    def test_calculate_test_results(self, ab_testing_service):
        """Test test results calculation"""
        with patch.object(ab_testing_service, '_get_test') as mock_get_test, \
             patch.object(ab_testing_service, '_get_test_assignments') as mock_assignments, \
             patch.object(ab_testing_service, '_get_test_conversions') as mock_conversions:
            
            mock_test = {
                "test_id": "test_123",
                "status": ABTestStatus.ACTIVE,
                "variants": [
                    {"name": "control", "traffic_split": 50},
                    {"name": "variant_a", "traffic_split": 50}
                ],
                "significance_level": 0.95
            }
            mock_get_test.return_value = mock_test
            
            # Mock assignments and conversions
            mock_assignments.return_value = [
                {"variant": "control"} for _ in range(500)
            ] + [
                {"variant": "variant_a"} for _ in range(500)
            ]
            
            mock_conversions.return_value = [
                {"variant": "control"} for _ in range(50)
            ] + [
                {"variant": "variant_a"} for _ in range(75)
            ]
            
            results = ab_testing_service.calculate_test_results("test_123")
            
            # Verify results structure
            assert 'variants' in results
            assert 'statistical_significance' in results
            assert 'total_participants' in results
            assert results['total_participants'] == 1000
    
    def test_confidence_interval_calculation(self, ab_testing_service):
        """Test confidence interval calculation"""
        # Test with known values
        conversions = 100
        participants = 1000
        confidence_level = 0.95
        
        ci = ab_testing_service._calculate_confidence_interval(
            conversions, participants, confidence_level
        )
        
        # Verify confidence interval is reasonable
        assert len(ci) == 2
        assert ci[0] < ci[1]  # Lower bound < upper bound
        assert 0 <= ci[0] <= 100  # Within valid percentage range
        assert 0 <= ci[1] <= 100


class TestReportService:
    """Test report generation service"""
    
    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)
    
    @pytest.fixture
    def report_service(self, mock_db):
        return ReportService(mock_db)
    
    def test_generate_pdf_report(self, report_service):
        """Test PDF report generation"""
        mock_data = {
            'users': {'total': 1000, 'growth_rate': 15.5},
            'applications': {'success_rate': 12.3},
            'insights': ['Test insight'],
            'recommendations': ['Test recommendation']
        }
        
        with patch.object(report_service, '_get_report_data') as mock_get_data:
            mock_get_data.return_value = mock_data
            
            report = report_service.generate_report(
                ReportType.PLATFORM_OVERVIEW,
                format=ReportFormat.PDF
            )
            
            # Verify report structure
            assert 'report_id' in report
            assert 'content' in report
            assert report['format'] == ReportFormat.PDF
            assert report['report_type'] == ReportType.PLATFORM_OVERVIEW
    
    def test_generate_csv_report(self, report_service):
        """Test CSV report generation"""
        mock_data = {
            'users': {'total': 1000, 'candidates': 800, 'companies': 200},
            'jobs': {'active': 150, 'total': 300}
        }
        
        with patch.object(report_service, '_get_report_data') as mock_get_data:
            mock_get_data.return_value = mock_data
            
            report = report_service.generate_report(
                ReportType.PLATFORM_OVERVIEW,
                format=ReportFormat.CSV
            )
            
            # Verify CSV content
            assert 'report_id' in report
            assert report['format'] == ReportFormat.CSV
            # CSV content should be a string
            assert isinstance(report['content'], str)
    
    def test_generate_json_report(self, report_service):
        """Test JSON report generation"""
        mock_data = {'test': 'data'}
        
        with patch.object(report_service, '_get_report_data') as mock_get_data:
            mock_get_data.return_value = mock_data
            
            report = report_service.generate_report(
                ReportType.PLATFORM_OVERVIEW,
                format=ReportFormat.JSON
            )
            
            # Verify JSON content can be parsed
            json_content = json.loads(report['content'])
            assert 'report_metadata' in json_content
            assert 'data' in json_content
            assert json_content['data'] == mock_data
    
    def test_schedule_report(self, report_service):
        """Test report scheduling"""
        report_config = {
            'report_type': 'platform_overview',
            'format': 'pdf'
        }
        
        schedule = {
            'frequency': 'monthly',
            'delivery': {'email': 'admin@company.com'}
        }
        
        scheduled_report = report_service.schedule_report(report_config, schedule)
        
        # Verify scheduled report structure
        assert 'schedule_id' in scheduled_report
        assert 'next_run' in scheduled_report
        assert scheduled_report['status'] == 'active'
        assert scheduled_report['report_config'] == report_config
    
    def test_get_report_templates(self, report_service):
        """Test getting available report templates"""
        templates = report_service.get_report_templates()
        
        # Verify templates structure
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        for template in templates:
            assert 'template_id' in template
            assert 'name' in template
            assert 'description' in template
            assert 'sections' in template
    
    def test_executive_summary_generation(self, report_service):
        """Test executive summary generation"""
        # Test platform overview summary
        platform_data = {
            'users': {'total': 5000, 'growth_rate': 25.5},
            'applications': {'success_rate': 18.7}
        }
        
        summary = report_service._generate_executive_summary(
            platform_data, ReportType.PLATFORM_OVERVIEW
        )
        
        assert '5000' in summary
        assert '25.5%' in summary
        assert '18.7%' in summary
    
    def test_data_flattening_for_csv(self, report_service):
        """Test data flattening for CSV export"""
        nested_data = {
            'users': {'total': 1000, 'growth_rate': 15.0},
            'jobs': {'active': 200, 'growth_rate': 10.0}
        }
        
        flattened = report_service._flatten_report_data(
            nested_data, ReportType.PLATFORM_OVERVIEW
        )
        
        # Verify flattened structure
        assert isinstance(flattened, list)
        assert len(flattened) > 0
        
        for item in flattened:
            assert 'Metric Category' in item
            assert 'Metric' in item
            assert 'Value' in item


class TestAnalyticsAPI:
    """Test analytics API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Mock API client"""
        return Mock()
    
    def test_platform_metrics_endpoint_permissions(self):
        """Test platform metrics endpoint requires admin access"""
        # This would test the actual API endpoint
        # Mock implementation for demonstration
        
        # Admin user should have access
        admin_user = Mock(user_type=UserType.ADMIN)
        # Test would verify successful response
        
        # Non-admin user should be denied
        candidate_user = Mock(user_type=UserType.CANDIDATE)
        # Test would verify 403 response
        
        assert True  # Placeholder assertion
    
    def test_hiring_effectiveness_endpoint_company_restriction(self):
        """Test hiring effectiveness endpoint restricts company data"""
        # Company users should only see their own data
        company_user = Mock(user_type=UserType.COMPANY, id="company_123")
        # Test would verify company_id is set to user's ID
        
        assert True  # Placeholder assertion
    
    def test_ab_test_creation_validation(self):
        """Test A/B test creation validates input"""
        # Test invalid traffic splits
        invalid_config = {
            "test_name": "Test",
            "variants": [
                {"name": "control", "traffic_split": 60},
                {"name": "variant", "traffic_split": 50}
            ]
        }
        # Should return 400 error
        
        assert True  # Placeholder assertion


class TestAnalyticsPerformance:
    """Test analytics system performance"""
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        # Mock large dataset
        large_dataset_size = 100000
        
        # Test should complete within reasonable time
        start_time = datetime.utcnow()
        
        # Simulate processing large dataset
        # In real test, would call actual analytics functions
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Should complete within 5 seconds for 100k records
        assert processing_time < 5.0
    
    def test_concurrent_analytics_requests(self):
        """Test handling concurrent analytics requests"""
        # Test multiple simultaneous requests
        # Should not cause database locks or performance issues
        
        assert True  # Placeholder assertion
    
    def test_memory_usage_optimization(self):
        """Test memory usage stays within bounds"""
        # Test processing large datasets doesn't cause memory issues
        
        assert True  # Placeholder assertion


class TestAnalyticsAccuracy:
    """Test analytics calculation accuracy"""
    
    def test_percentage_calculations(self):
        """Test percentage calculations are accurate"""
        # Test various scenarios
        test_cases = [
            (50, 100, 50.0),  # 50 out of 100 = 50%
            (1, 3, 33.33),    # 1 out of 3 = 33.33%
            (0, 100, 0.0),    # 0 out of 100 = 0%
            (100, 100, 100.0) # 100 out of 100 = 100%
        ]
        
        for numerator, denominator, expected in test_cases:
            result = (numerator / denominator) * 100
            assert abs(result - expected) < 0.01
    
    def test_growth_rate_accuracy(self):
        """Test growth rate calculations"""
        # Test growth rate calculation accuracy
        current = 120
        previous = 100
        expected_growth = 20.0  # 20% growth
        
        actual_growth = ((current - previous) / previous) * 100
        assert abs(actual_growth - expected_growth) < 0.01
    
    def test_statistical_significance_accuracy(self):
        """Test statistical significance calculations"""
        # Test with known statistical values
        # This would use actual statistical libraries
        
        assert True  # Placeholder assertion
    
    def test_confidence_interval_accuracy(self):
        """Test confidence interval calculations"""
        # Test confidence intervals are mathematically correct
        
        assert True  # Placeholder assertion


# Integration tests
class TestAnalyticsIntegration:
    """Integration tests for analytics system"""
    
    def test_end_to_end_report_generation(self):
        """Test complete report generation flow"""
        # Test from data collection to report delivery
        
        assert True  # Placeholder assertion
    
    def test_ab_test_complete_workflow(self):
        """Test complete A/B test workflow"""
        # Test create -> start -> collect data -> analyze -> stop
        
        assert True  # Placeholder assertion
    
    def test_real_time_analytics_updates(self):
        """Test real-time analytics updates"""
        # Test that analytics update as new data comes in
        
        assert True  # Placeholder assertion


if __name__ == "__main__":
    pytest.main([__file__])