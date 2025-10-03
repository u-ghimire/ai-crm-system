# modules/workflow_automation.py
"""
Workflow Automation Module - Automates repetitive tasks and scheduling
Handles reminders, follow-ups, and report generation
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import threading
import time

class WorkflowAutomation:
    def __init__(self, db=None):
        """Initialize workflow automation"""
        self.db = db
        self.active_workflows = []
        self.scheduler_thread = None
        self.running = False
        
        # Email configuration (placeholder)
        self.smtp_config = {
            'server': 'smtp.gmail.com',
            'port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password'
        }
        
        # Workflow templates
        self.workflow_templates = {
            'new_lead': self._new_lead_workflow,
            'follow_up': self._follow_up_workflow,
            'nurture': self._nurture_workflow,
            'win_back': self._win_back_workflow
        }
    
    def start_scheduler(self):
        """Start the background scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
    
    def _run_scheduler(self):
        """Run the scheduler in background"""
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def schedule_follow_up(self, customer_id: int, priority: str = 'medium', days_ahead: int = None) -> int:
        """Schedule a follow-up task"""
        if days_ahead is None:
            days_ahead = {
                'high': 1,
                'medium': 3,
                'low': 7
            }.get(priority, 3)
        
        due_date = datetime.now() + timedelta(days=days_ahead)
        
        task_data = {
            'customer_id': customer_id,
            'title': f'Follow up with customer (Priority: {priority})',
            'description': 'Scheduled follow-up based on lead score',
            'due_date': due_date.isoformat(),
            'priority': priority,
            'type': 'follow-up',
            'status': 'pending'
        }
        
        if self.db:
            return self.db.add_task(task_data)
        
        return 0
    
    def schedule_task(self, task_data: Dict) -> int:
        """Schedule a custom task"""
        # Validate task data
        required_fields = ['title', 'due_date']
        for field in required_fields:
            if field not in task_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Set defaults
        task_data.setdefault('priority', 'medium')
        task_data.setdefault('type', 'general')
        task_data.setdefault('status', 'pending')
        
        if self.db:
            return self.db.add_task(task_data)
        
        return 0
    
    def get_user_reminders(self, user_id: int) -> List[Dict]:
        """Get pending reminders for a user"""
        if self.db:
            tasks = self.db.get_user_tasks(user_id, status='pending')
            
            # Filter for due/overdue tasks
            now = datetime.now()
            reminders = []
            
            for task in tasks:
                due_date = datetime.fromisoformat(task['due_date'])
                task['is_overdue'] = due_date < now
                task['due_in_days'] = (due_date - now).days
                
                # Include if due within 7 days or overdue
                if task['is_overdue'] or task['due_in_days'] <= 7:
                    reminders.append(task)
            
            # Sort by due date
            reminders.sort(key=lambda x: x['due_date'])
            
            return reminders
        
        return []
    
    def create_workflow(self, workflow_type: str, customer_id: int, params: Dict = None) -> Dict:
        """Create and execute a workflow"""
        if workflow_type not in self.workflow_templates:
            raise ValueError(f"Unknown workflow type: {workflow_type}")
        
        workflow = {
            'id': len(self.active_workflows) + 1,
            'type': workflow_type,
            'customer_id': customer_id,
            'params': params or {},
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'steps_completed': []
        }
        
        self.active_workflows.append(workflow)
        
        # Execute workflow
        workflow_func = self.workflow_templates[workflow_type]
        workflow_func(workflow)
        
        return workflow
    
    def _new_lead_workflow(self, workflow: Dict):
        """Workflow for new leads"""
        customer_id = workflow['customer_id']
        
        # Step 1: Send welcome email
        self._queue_email(
            customer_id,
            'Welcome! Thanks for your interest',
            'welcome_template'
        )
        workflow['steps_completed'].append('welcome_email')
        
        # Step 2: Schedule initial follow-up
        self.schedule_follow_up(customer_id, priority='high', days_ahead=1)
        workflow['steps_completed'].append('initial_follow_up')
        
        # Step 3: Add to nurture campaign
        self._add_to_campaign(customer_id, 'new_lead_nurture')
        workflow['steps_completed'].append('nurture_campaign')
        
        # Step 4: Notify sales team
        self._notify_team(customer_id, 'New lead assigned')
        workflow['steps_completed'].append('team_notification')
    
    def _follow_up_workflow(self, workflow: Dict):
        """Workflow for follow-ups"""
        customer_id = workflow['customer_id']
        params = workflow.get('params', {})
        
        # Step 1: Check interaction history
        if self.db:
            interactions = self.db.get_customer_interactions(customer_id)
            days_since_last = self._days_since_last_interaction(interactions)
            
            if days_since_last > 7:
                # Send re-engagement email
                self._queue_email(
                    customer_id,
                    'We miss you! Let\'s reconnect',
                    're_engagement_template'
                )
                workflow['steps_completed'].append('re_engagement_email')
            
            # Step 2: Schedule next follow-up based on engagement
            if days_since_last > 14:
                priority = 'high'
            elif days_since_last > 7:
                priority = 'medium'
            else:
                priority = 'low'
            
            self.schedule_follow_up(customer_id, priority=priority)
            workflow['steps_completed'].append('next_follow_up_scheduled')
    
    def _nurture_workflow(self, workflow: Dict):
        """Workflow for lead nurturing"""
        customer_id = workflow['customer_id']
        
        # Create a series of educational emails
        email_series = [
            {'day': 0, 'subject': 'Getting Started Guide', 'template': 'getting_started'},
            {'day': 3, 'subject': 'Top 5 CRM Best Practices', 'template': 'best_practices'},
            {'day': 7, 'subject': 'Customer Success Story', 'template': 'case_study'},
            {'day': 14, 'subject': 'Exclusive Offer Inside', 'template': 'special_offer'},
            {'day': 21, 'subject': 'Schedule Your Demo', 'template': 'demo_invite'}
        ]
        
        for email in email_series:
            self._schedule_email(
                customer_id,
                email['subject'],
                email['template'],
                days_ahead=email['day']
            )
        
        workflow['steps_completed'].append('nurture_series_scheduled')
    
    def _win_back_workflow(self, workflow: Dict):
        """Workflow for winning back inactive customers"""
        customer_id = workflow['customer_id']
        
        # Step 1: Send win-back email
        self._queue_email(
            customer_id,
            'We want you back! Special offer inside',
            'win_back_template'
        )
        workflow['steps_completed'].append('win_back_email')
        
        # Step 2: Create special offer
        self._create_special_offer(customer_id)
        workflow['steps_completed'].append('special_offer_created')
        
        # Step 3: Alert sales for personal outreach
        self._notify_team(
            customer_id,
            'Win-back opportunity - personal outreach recommended'
        )
        workflow['steps_completed'].append('personal_outreach_alert')
    
    def generate_report(self, report_type: str = 'weekly') -> Dict:
        """Generate automated reports"""
        report = {
            'type': report_type,
            'generated_at': datetime.now().isoformat(),
            'period': self._get_report_period(report_type),
            'metrics': {},
            'insights': [],
            'recommendations': []
        }
        
        if self.db:
            # Gather metrics
            report['metrics'] = {
                'new_customers': self._get_new_customers_count(report_type),
                'total_interactions': self._get_interactions_count(report_type),
                'conversion_rate': self.db.get_conversion_rate(),
                'revenue': self.db.get_monthly_revenue(),
                'active_leads': self.db.get_active_leads_count(),
                'top_performers': self.db.get_top_leads(5)
            }
            
            # Generate insights
            report['insights'] = self._generate_report_insights(report['metrics'])
            
            # Generate recommendations
            report['recommendations'] = self._generate_report_recommendations(report['metrics'])
        
        return report
    
    def automate_data_entry(self, source: str, data: Any) -> Dict:
        """Automate data entry from various sources"""
        result = {
            'source': source,
            'processed_at': datetime.now().isoformat(),
            'records_processed': 0,
            'errors': []
        }
        
        if source == 'email':
            result = self._process_email_data(data, result)
        elif source == 'form':
            result = self._process_form_data(data, result)
        elif source == 'api':
            result = self._process_api_data(data, result)
        elif source == 'csv':
            result = self._process_csv_data(data, result)
        
        return result
    
    def set_up_alerts(self, alert_config: Dict) -> Dict:
        """Set up automated alerts"""
        alert = {
            'id': len(self.active_workflows) + 1000,  # Different ID space
            'type': alert_config.get('type', 'threshold'),
            'condition': alert_config.get('condition'),
            'threshold': alert_config.get('threshold'),
            'recipients': alert_config.get('recipients', []),
            'status': 'active',
            'created_at': datetime.now().isoformat()
        }
        
        # Schedule alert checking
        if alert['type'] == 'threshold':
            schedule.every().hour.do(self._check_threshold_alert, alert)
        elif alert['type'] == 'time_based':
            schedule.every().day.at(alert_config.get('time', '09:00')).do(
                self._check_time_based_alert, alert
            )
        
        return alert
    
    # Helper methods
    def _queue_email(self, customer_id: int, subject: str, template: str):
        """Queue an email for sending"""
        # In production, this would actually send emails
        print(f"Email queued - Customer: {customer_id}, Subject: {subject}, Template: {template}")
    
    def _schedule_email(self, customer_id: int, subject: str, template: str, days_ahead: int):
        """Schedule an email for future sending"""
        send_date = datetime.now() + timedelta(days=days_ahead)
        print(f"Email scheduled for {send_date} - Customer: {customer_id}, Subject: {subject}")
    
    def _add_to_campaign(self, customer_id: int, campaign: str):
        """Add customer to marketing campaign"""
        print(f"Customer {customer_id} added to campaign: {campaign}")
    
    def _notify_team(self, customer_id: int, message: str):
        """Notify sales team"""
        print(f"Team notification - Customer: {customer_id}, Message: {message}")
    
    def _create_special_offer(self, customer_id: int):
        """Create special offer for customer"""
        offer = {
            'customer_id': customer_id,
            'discount': '20%',
            'valid_until': (datetime.now() + timedelta(days=30)).isoformat()
        }
        print(f"Special offer created for customer {customer_id}: {offer}")
    
    def _days_since_last_interaction(self, interactions: List[Dict]) -> int:
        """Calculate days since last interaction"""
        if not interactions:
            return 999  # Large number if no interactions
        
        latest = max(interactions, key=lambda x: x.get('created_at', ''))
        if latest and latest.get('created_at'):
            last_date = datetime.fromisoformat(latest['created_at'])
            return (datetime.now() - last_date).days
        
        return 999
    
    def _get_report_period(self, report_type: str) -> Dict:
        """Get report period dates"""
        end_date = datetime.now()
        
        if report_type == 'daily':
            start_date = end_date - timedelta(days=1)
        elif report_type == 'weekly':
            start_date = end_date - timedelta(weeks=1)
        elif report_type == 'monthly':
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=90)
        
        return {
            'start': start_date.isoformat(),
            'end': end_date.isoformat()
        }
    
    def _get_new_customers_count(self, report_type: str) -> int:
        """Get count of new customers for period"""
        # Simplified - in production would query database with date filter
        if self.db:
            return len(self.db.get_all_customers())
        return 0
    
    def _get_interactions_count(self, report_type: str) -> int:
        """Get count of interactions for period"""
        if self.db:
            return len(self.db.get_all_interactions())
        return 0
    
    def _generate_report_insights(self, metrics: Dict) -> List[str]:
        """Generate insights from metrics"""
        insights = []
        
        if metrics.get('conversion_rate', 0) > 20:
            insights.append("Excellent conversion rate above 20%")
        elif metrics.get('conversion_rate', 0) < 10:
            insights.append("Conversion rate below target - focus on lead quality")
        
        if metrics.get('active_leads', 0) > 50:
            insights.append("High number of active leads - ensure adequate follow-up")
        
        if metrics.get('revenue', 0) > 100000:
            insights.append("Strong revenue performance this period")
        
        return insights if insights else ["Performance metrics within normal range"]
    
    def _generate_report_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations from metrics"""
        recommendations = []
        
        if metrics.get('conversion_rate', 0) < 15:
            recommendations.append("Implement lead scoring to improve qualification")
        
        if metrics.get('active_leads', 0) > 100:
            recommendations.append("Consider increasing sales team capacity")
        
        if metrics.get('new_customers', 0) < 10:
            recommendations.append("Increase marketing efforts to generate more leads")
        
        return recommendations if recommendations else ["Maintain current strategies"]
    
    def _process_email_data(self, data: Any, result: Dict) -> Dict:
        """Process data from email source"""
        # Parse email for customer information
        # This would integrate with email parsing services
        result['records_processed'] = 1
        return result
    
    def _process_form_data(self, data: Any, result: Dict) -> Dict:
        """Process form submission data"""
        if self.db and isinstance(data, dict):
            try:
                customer_id = self.db.add_customer(data)
                result['records_processed'] = 1
                result['customer_id'] = customer_id
            except Exception as e:
                result['errors'].append(str(e))
        
        return result
    
    def _process_api_data(self, data: Any, result: Dict) -> Dict:
        """Process API data"""
        if isinstance(data, list):
            for record in data:
                if self.db:
                    try:
                        self.db.add_customer(record)
                        result['records_processed'] += 1
                    except Exception as e:
                        result['errors'].append(f"Record error: {str(e)}")
        
        return result
    
    def _process_csv_data(self, data: Any, result: Dict) -> Dict:
        """Process CSV data"""
        # This would parse CSV and import records
        result['records_processed'] = 0
        return result
    
    def _check_threshold_alert(self, alert: Dict):
        """Check threshold-based alerts"""
        if alert['condition'] == 'low_conversion':
            if self.db:
                conversion_rate = self.db.get_conversion_rate()
                if conversion_rate < alert['threshold']:
                    self._send_alert(alert, f"Low conversion rate: {conversion_rate}%")
    
    def _check_time_based_alert(self, alert: Dict):
        """Check time-based alerts"""
        # Send daily/weekly summaries
        self._send_alert(alert, "Scheduled alert triggered")
    
    def _send_alert(self, alert: Dict, message: str):
        """Send alert to recipients"""
        print(f"Alert sent to {alert['recipients']}: {message}")