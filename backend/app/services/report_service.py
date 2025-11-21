"""
Report Generation Service for AI-HR Platform

Provides automated report generation capabilities including:
- PDF and CSV report generation
- Scheduled report delivery
- Custom report templates
- Data visualization in reports
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import json
import io
import base64
from pathlib import Path

# For report generation (would need to install these packages)
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from io import BytesIO

from .analytics_service import AnalyticsService, TimeRange


class ReportFormat(str, Enum):
    PDF = "pdf"
    CSV = "csv"
    XLSX = "xlsx"
    JSON = "json"


class ReportType(str, Enum):
    PLATFORM_OVERVIEW = "platform_overview"
    HIRING_EFFECTIVENESS = "hiring_effectiveness"
    CANDIDATE_INSIGHTS = "candidate_insights"
    COMPANY_PERFORMANCE = "company_performance"
    CUSTOM = "custom"


class ReportService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)

    def generate_report(self, report_type: ReportType, entity_id: Optional[str] = None,
                       time_range: TimeRange = TimeRange.MONTHLY,
                       format: ReportFormat = ReportFormat.PDF,
                       custom_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a comprehensive report"""
        
        # Get report data
        report_data = self._get_report_data(report_type, entity_id, time_range)
        
        # Generate report based on format
        if format == ReportFormat.PDF:
            report_content = self._generate_pdf_report(report_data, report_type)
        elif format == ReportFormat.CSV:
            report_content = self._generate_csv_report(report_data, report_type)
        elif format == ReportFormat.XLSX:
            report_content = self._generate_xlsx_report(report_data, report_type)
        elif format == ReportFormat.JSON:
            report_content = self._generate_json_report(report_data, report_type)
        else:
            raise ValueError(f"Unsupported report format: {format}")
        
        report_id = f"report_{report_type}_{int(datetime.utcnow().timestamp())}"
        
        return {
            "report_id": report_id,
            "report_type": report_type,
            "format": format,
            "generated_at": datetime.utcnow().isoformat(),
            "entity_id": entity_id,
            "time_range": time_range,
            "content": report_content,
            "download_url": f"/analytics/reports/{report_id}/download",
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }

    def schedule_report(self, report_config: Dict[str, Any], 
                       schedule: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule automated report generation"""
        
        schedule_id = f"schedule_{int(datetime.utcnow().timestamp())}"
        
        scheduled_report = {
            "schedule_id": schedule_id,
            "report_config": report_config,
            "schedule": schedule,
            "created_at": datetime.utcnow().isoformat(),
            "next_run": self._calculate_next_run(schedule),
            "status": "active",
            "delivery_config": schedule.get("delivery", {})
        }
        
        # In production, save to database and set up cron job
        return scheduled_report

    def get_report_templates(self) -> List[Dict[str, Any]]:
        """Get available report templates"""
        templates = [
            {
                "template_id": "executive_summary",
                "name": "Executive Summary",
                "description": "High-level overview of key metrics and trends",
                "report_types": ["platform_overview", "company_performance"],
                "sections": ["key_metrics", "trends", "insights", "recommendations"]
            },
            {
                "template_id": "detailed_analytics",
                "name": "Detailed Analytics Report",
                "description": "Comprehensive analysis with charts and detailed breakdowns",
                "report_types": ["hiring_effectiveness", "candidate_insights"],
                "sections": ["overview", "detailed_metrics", "charts", "analysis", "recommendations"]
            },
            {
                "template_id": "performance_dashboard",
                "name": "Performance Dashboard",
                "description": "Visual dashboard-style report with key performance indicators",
                "report_types": ["company_performance"],
                "sections": ["kpi_summary", "performance_charts", "benchmarks", "action_items"]
            }
        ]
        
        return templates

    def create_custom_template(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom report template"""
        template_id = f"custom_{int(datetime.utcnow().timestamp())}"
        
        template = {
            "template_id": template_id,
            "name": template_config["name"],
            "description": template_config.get("description", ""),
            "sections": template_config["sections"],
            "styling": template_config.get("styling", {}),
            "created_at": datetime.utcnow().isoformat(),
            "created_by": template_config.get("created_by"),
            "is_custom": True
        }
        
        # In production, save to database
        return template

    # Private methods for report generation
    def _get_report_data(self, report_type: ReportType, entity_id: Optional[str],
                        time_range: TimeRange) -> Dict[str, Any]:
        """Get data for report generation"""
        
        if report_type == ReportType.PLATFORM_OVERVIEW:
            return self.analytics_service.get_platform_metrics()
        elif report_type == ReportType.HIRING_EFFECTIVENESS:
            return self.analytics_service.get_hiring_effectiveness_metrics(entity_id)
        elif report_type == ReportType.CANDIDATE_INSIGHTS:
            return self.analytics_service.get_candidate_success_insights(entity_id)
        elif report_type == ReportType.COMPANY_PERFORMANCE:
            return self.analytics_service.get_performance_dashboard_data(entity_id, time_range)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _generate_pdf_report(self, data: Dict[str, Any], report_type: ReportType) -> str:
        """Generate PDF report"""
        if not REPORTLAB_AVAILABLE:
            return "PDF generation not available - reportlab not installed"
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        
        title = f"{report_type.replace('_', ' ').title()} Report"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))
        
        # Generated date
        date_text = f"Generated on: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}"
        story.append(Paragraph(date_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        summary = self._generate_executive_summary(data, report_type)
        story.append(Paragraph(summary, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Key Metrics Table
        if report_type == ReportType.PLATFORM_OVERVIEW:
            story.extend(self._create_platform_metrics_section(data, styles))
        elif report_type == ReportType.HIRING_EFFECTIVENESS:
            story.extend(self._create_hiring_metrics_section(data, styles))
        elif report_type == ReportType.CANDIDATE_INSIGHTS:
            story.extend(self._create_candidate_metrics_section(data, styles))
        elif report_type == ReportType.COMPANY_PERFORMANCE:
            story.extend(self._create_company_metrics_section(data, styles))
        
        # Charts section
        story.append(Paragraph("Visual Analytics", styles['Heading2']))
        chart_images = self._generate_charts(data, report_type)
        for chart_image in chart_images:
            story.append(chart_image)
            story.append(Spacer(1, 12))
        
        # Insights and Recommendations
        story.append(Paragraph("Insights & Recommendations", styles['Heading2']))
        insights = data.get('insights', ['No specific insights available'])
        recommendations = data.get('recommendations', ['No specific recommendations available'])
        
        story.append(Paragraph("Key Insights:", styles['Heading3']))
        for insight in insights:
            story.append(Paragraph(f"• {insight}", styles['Normal']))
        
        story.append(Spacer(1, 12))
        story.append(Paragraph("Recommendations:", styles['Heading3']))
        for recommendation in recommendations:
            story.append(Paragraph(f"• {recommendation}", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        # Return base64 encoded PDF
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return base64.b64encode(pdf_content).decode('utf-8')

    def _generate_csv_report(self, data: Dict[str, Any], report_type: ReportType) -> str:
        """Generate CSV report"""
        if not PANDAS_AVAILABLE:
            return "CSV generation not available - pandas not installed"
        
        # Flatten data for CSV format
        flattened_data = self._flatten_report_data(data, report_type)
        
        # Create DataFrame
        df = pd.DataFrame(flattened_data)
        
        # Convert to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        
        return csv_buffer.getvalue()

    def _generate_xlsx_report(self, data: Dict[str, Any], report_type: ReportType) -> str:
        """Generate Excel report"""
        if not PANDAS_AVAILABLE:
            return "Excel generation not available - pandas not installed"
        
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = self._create_summary_sheet_data(data, report_type)
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Detailed data sheets based on report type
            if report_type == ReportType.PLATFORM_OVERVIEW:
                self._add_platform_sheets(writer, data)
            elif report_type == ReportType.HIRING_EFFECTIVENESS:
                self._add_hiring_sheets(writer, data)
            elif report_type == ReportType.CANDIDATE_INSIGHTS:
                self._add_candidate_sheets(writer, data)
            elif report_type == ReportType.COMPANY_PERFORMANCE:
                self._add_company_sheets(writer, data)
        
        buffer.seek(0)
        excel_content = buffer.getvalue()
        
        return base64.b64encode(excel_content).decode('utf-8')

    def _generate_json_report(self, data: Dict[str, Any], report_type: ReportType) -> str:
        """Generate JSON report"""
        
        report_json = {
            "report_metadata": {
                "type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            },
            "data": data,
            "summary": self._generate_executive_summary(data, report_type)
        }
        
        return json.dumps(report_json, indent=2, default=str)

    def _generate_executive_summary(self, data: Dict[str, Any], report_type: ReportType) -> str:
        """Generate executive summary text"""
        
        if report_type == ReportType.PLATFORM_OVERVIEW:
            users = data.get('users', {})
            applications = data.get('applications', {})
            return f"Platform currently has {users.get('total', 0)} total users with {users.get('growth_rate', 0)}% growth. Application success rate is {applications.get('success_rate', 0)}%."
        
        elif report_type == ReportType.HIRING_EFFECTIVENESS:
            hiring_rate = data.get('hiring_rate', 0)
            time_to_hire = data.get('average_time_to_hire', 0)
            return f"Current hiring rate is {hiring_rate}% with an average time to hire of {time_to_hire} days."
        
        elif report_type == ReportType.CANDIDATE_INSIGHTS:
            total_candidates = data.get('total_candidates', 0)
            success_metrics = data.get('success_metrics', {})
            success_rate = success_metrics.get('application_success_rate', 0)
            return f"Analysis of {total_candidates} candidates shows an average application success rate of {success_rate}%."
        
        elif report_type == ReportType.COMPANY_PERFORMANCE:
            hiring_metrics = data.get('hiring_metrics', {})
            roi_metrics = data.get('roi_metrics', {})
            return f"Company performance shows {hiring_metrics.get('hiring_rate', 0)}% hiring rate with {roi_metrics.get('roi_percentage', 0)}% ROI."
        
        return "Executive summary not available for this report type."

    def _create_platform_metrics_section(self, data: Dict[str, Any], styles) -> List:
        """Create platform metrics section for PDF"""
        elements = []
        
        elements.append(Paragraph("Platform Metrics", styles['Heading2']))
        
        # Create metrics table
        users = data.get('users', {})
        jobs = data.get('jobs', {})
        applications = data.get('applications', {})
        
        table_data = [
            ['Metric', 'Value', 'Growth Rate'],
            ['Total Users', f"{users.get('total', 0):,}", f"{users.get('growth_rate', 0)}%"],
            ['Active Jobs', f"{jobs.get('active', 0):,}", f"{jobs.get('growth_rate', 0)}%"],
            ['Total Applications', f"{applications.get('total', 0):,}", f"{applications.get('growth_rate', 0)}%"],
            ['Success Rate', f"{applications.get('success_rate', 0)}%", "-"]
        ]
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    def _create_hiring_metrics_section(self, data: Dict[str, Any], styles) -> List:
        """Create hiring metrics section for PDF"""
        elements = []
        
        elements.append(Paragraph("Hiring Effectiveness Metrics", styles['Heading2']))
        
        table_data = [
            ['Metric', 'Value'],
            ['Total Applications', f"{data.get('total_applications', 0):,}"],
            ['Hiring Rate', f"{data.get('hiring_rate', 0)}%"],
            ['Avg Time to Hire', f"{data.get('average_time_to_hire', 0)} days"],
            ['Cost per Hire', f"${data.get('cost_per_hire', 0):,}"],
            ['Quality of Hire', f"{data.get('quality_of_hire', 0)}/5.0"]
        ]
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    def _create_candidate_metrics_section(self, data: Dict[str, Any], styles) -> List:
        """Create candidate metrics section for PDF"""
        elements = []
        
        elements.append(Paragraph("Candidate Success Metrics", styles['Heading2']))
        
        success_metrics = data.get('success_metrics', {})
        
        table_data = [
            ['Metric', 'Value'],
            ['Total Candidates', f"{data.get('total_candidates', 0):,}"],
            ['Application Success Rate', f"{success_metrics.get('application_success_rate', 0)}%"],
            ['Avg Applications per Candidate', f"{success_metrics.get('average_applications_per_candidate', 0):.1f}"],
            ['Interview Conversion Rate', f"{success_metrics.get('interview_conversion_rate', 0)}%"]
        ]
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    def _create_company_metrics_section(self, data: Dict[str, Any], styles) -> List:
        """Create company metrics section for PDF"""
        elements = []
        
        elements.append(Paragraph("Company Performance Metrics", styles['Heading2']))
        
        hiring_metrics = data.get('hiring_metrics', {})
        roi_metrics = data.get('roi_metrics', {})
        
        table_data = [
            ['Metric', 'Value'],
            ['Hiring Rate', f"{hiring_metrics.get('hiring_rate', 0)}%"],
            ['Time to Hire', f"{hiring_metrics.get('average_time_to_hire', 0)} days"],
            ['Total Hires', f"{roi_metrics.get('total_hires', 0):,}"],
            ['ROI Percentage', f"{roi_metrics.get('roi_percentage', 0)}%"],
            ['Payback Period', f"{roi_metrics.get('payback_period_months', 0)} months"]
        ]
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements

    def _generate_charts(self, data: Dict[str, Any], report_type: ReportType) -> List:
        """Generate charts for PDF report"""
        charts = []
        
        if not MATPLOTLIB_AVAILABLE:
            return charts
        
        # Create sample charts using matplotlib
        try:
            plt.style.use('seaborn-v0_8')
        except:
            # Fallback if seaborn style not available
            pass
        
        if report_type == ReportType.PLATFORM_OVERVIEW:
            # User growth chart
            fig, ax = plt.subplots(figsize=(8, 4))
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
            users = [1000, 1200, 1400, 1650, 1900, 2100]
            ax.plot(months, users, marker='o', linewidth=2, markersize=6)
            ax.set_title('User Growth Trend', fontsize=14, fontweight='bold')
            ax.set_ylabel('Total Users')
            ax.grid(True, alpha=0.3)
            
            # Save chart as image
            chart_buffer = BytesIO()
            plt.savefig(chart_buffer, format='png', dpi=150, bbox_inches='tight')
            chart_buffer.seek(0)
            
            # Convert to ReportLab Image
            if REPORTLAB_AVAILABLE:
                chart_image = Image(chart_buffer, width=6*inch, height=3*inch)
                charts.append(chart_image)
            
            plt.close()
        
        return charts

    def _flatten_report_data(self, data: Dict[str, Any], report_type: ReportType) -> List[Dict[str, Any]]:
        """Flatten nested data for CSV export"""
        flattened = []
        
        if report_type == ReportType.PLATFORM_OVERVIEW:
            users = data.get('users', {})
            jobs = data.get('jobs', {})
            applications = data.get('applications', {})
            
            flattened.append({
                'Metric Category': 'Users',
                'Metric': 'Total Users',
                'Value': users.get('total', 0),
                'Growth Rate': f"{users.get('growth_rate', 0)}%"
            })
            flattened.append({
                'Metric Category': 'Jobs',
                'Metric': 'Active Jobs',
                'Value': jobs.get('active', 0),
                'Growth Rate': f"{jobs.get('growth_rate', 0)}%"
            })
            flattened.append({
                'Metric Category': 'Applications',
                'Metric': 'Success Rate',
                'Value': f"{applications.get('success_rate', 0)}%",
                'Growth Rate': f"{applications.get('growth_rate', 0)}%"
            })
        
        return flattened

    def _create_summary_sheet_data(self, data: Dict[str, Any], report_type: ReportType) -> List[Dict[str, Any]]:
        """Create summary data for Excel sheet"""
        return self._flatten_report_data(data, report_type)

    def _add_platform_sheets(self, writer, data: Dict[str, Any]):
        """Add platform-specific sheets to Excel report"""
        # Users sheet
        users_data = [
            {'Metric': 'Total Users', 'Value': data.get('users', {}).get('total', 0)},
            {'Metric': 'Candidates', 'Value': data.get('users', {}).get('candidates', 0)},
            {'Metric': 'Companies', 'Value': data.get('users', {}).get('companies', 0)}
        ]
        pd.DataFrame(users_data).to_excel(writer, sheet_name='Users', index=False)

    def _add_hiring_sheets(self, writer, data: Dict[str, Any]):
        """Add hiring-specific sheets to Excel report"""
        # Funnel metrics
        funnel_data = []
        funnel_metrics = data.get('funnel_metrics', {})
        for stage, metrics in funnel_metrics.items():
            if isinstance(metrics, dict):
                funnel_data.append({
                    'Stage': stage.title(),
                    'Count': metrics.get('count', 0),
                    'Percentage': f"{metrics.get('percentage', 0)}%"
                })
        
        if funnel_data:
            pd.DataFrame(funnel_data).to_excel(writer, sheet_name='Hiring Funnel', index=False)

    def _add_candidate_sheets(self, writer, data: Dict[str, Any]):
        """Add candidate-specific sheets to Excel report"""
        # Skill trends
        skill_data = []
        skill_trends = data.get('skill_trends', {})
        for skill, trend in skill_trends.items():
            if isinstance(trend, dict):
                skill_data.append({
                    'Skill': skill,
                    'Average Score': trend.get('average_score', 0),
                    'Trend': trend.get('improvement_trend', 'stable'),
                    'Candidate Count': trend.get('candidate_count', 0)
                })
        
        if skill_data:
            pd.DataFrame(skill_data).to_excel(writer, sheet_name='Skill Trends', index=False)

    def _add_company_sheets(self, writer, data: Dict[str, Any]):
        """Add company-specific sheets to Excel report"""
        # Job performance
        job_performance = data.get('job_performance', {}).get('performance', [])
        if job_performance:
            pd.DataFrame(job_performance).to_excel(writer, sheet_name='Job Performance', index=False)

    def _calculate_next_run(self, schedule: Dict[str, Any]) -> str:
        """Calculate next scheduled run time"""
        frequency = schedule.get('frequency', 'monthly')
        
        if frequency == 'daily':
            next_run = datetime.utcnow() + timedelta(days=1)
        elif frequency == 'weekly':
            next_run = datetime.utcnow() + timedelta(weeks=1)
        elif frequency == 'monthly':
            next_run = datetime.utcnow() + timedelta(days=30)
        else:
            next_run = datetime.utcnow() + timedelta(days=30)
        
        return next_run.isoformat()