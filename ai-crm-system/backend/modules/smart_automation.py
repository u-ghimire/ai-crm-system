"""
Smart Automation Engine - AI-powered task automation and data enrichment
Auto-generates tasks, reminders, and enriches contact/company data
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .groq_ai import GroqAI
from .db_helper import get_db

class SmartAutomation:
    def __init__(self, ai_model: GroqAI):
        """Initialize smart automation engine"""
        self.ai_model = ai_model
        
        # Task generation rules
        self.activity_task_rules = {
            'email': {
                'follow_up_days': 3,
                'task_template': 'Follow up on email sent to {contact}'
            },
            'call': {
                'follow_up_days': 2,
                'task_template': 'Follow up on call with {contact}'
            },
            'meeting': {
                'follow_up_days': 1,
                'task_template': 'Send meeting recap and next steps to {contact}'
            },
            'demo': {
                'follow_up_days': 1,
                'task_template': 'Follow up on demo presented to {contact}'
            }
        }
        
        # Smart reminder thresholds
        self.reminder_thresholds = {
            'no_contact_15_days': 15,
            'no_contact_30_days': 30,
            'deal_stalled_14_days': 14,
            'expected_close_approaching': 7
        }
    
    def auto_generate_follow_up_tasks(self, activity_id: int = None, activity_data: Dict = None) -> Dict:
        """
        Automatically generate follow-up tasks after activities
        
        Args:
            activity_id: Activity ID to generate tasks for
            activity_data: Activity data dict (if already loaded)
        
        Returns:
            Dict with generated tasks
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get activity data if not provided
            if not activity_data and activity_id:
                cursor.execute('''
                    SELECT i.*, 
                           c.name as contact_name,
                           c.company as company_name,
                           o.title as deal_title
                    FROM interactions i
                    LEFT JOIN customers c ON i.customer_id = c.id
                    LEFT JOIN opportunities o ON i.customer_id = o.customer_id
                    WHERE i.id = ?
                ''', (activity_id,))
                activity_data = dict(cursor.fetchone() or {})
            
            if not activity_data:
                return {'error': 'Activity not found'}
            
            activity_type = (activity_data.get('type', 'note') or 'note').lower()
            contact_name = activity_data.get('contact_name', 'contact')
            company_name = activity_data.get('company_name', '')
            deal_title = activity_data.get('deal_title', '')
            
            # Get task generation rule
            rule = self.activity_task_rules.get(activity_type, {
                'follow_up_days': 3,
                'task_template': 'Follow up on recent interaction with {contact}'
            })
            
            # Generate task with AI enhancement
            base_task = rule['task_template'].format(contact=contact_name)
            enhanced_task = self._enhance_task_with_ai(base_task, activity_data)
            
            # Calculate due date
            due_date = datetime.now() + timedelta(days=rule['follow_up_days'])
            
            # Create task
            cursor.execute('''
                INSERT INTO tasks (title, description, due_date, priority, status, 
                                 contact_id, company_id, deal_id, auto_generated, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                enhanced_task['title'],
                enhanced_task['description'],
                due_date.strftime('%Y-%m-%d'),
                enhanced_task['priority'],
                'pending',
                activity_data.get('contact_id'),
                activity_data.get('company_id'),
                activity_data.get('deal_id'),
                1  # Mark as auto-generated
            ))
            
            db.commit()
            task_id = cursor.lastrowid
            
            return {
                'success': True,
                'task_id': task_id,
                'task': enhanced_task,
                'due_date': due_date.strftime('%Y-%m-%d'),
                'activity_type': activity_type,
                'message': f"Auto-generated follow-up task for {activity_type}"
            }
            
        except Exception as e:
            print(f"Auto task generation error: {e}")
            return {'error': str(e)}
    
    def _enhance_task_with_ai(self, base_task: str, activity_data: Dict) -> Dict:
        """Use AI to enhance task with context-aware details"""
        activity_type = activity_data.get('type', 'note')
        activity_notes = activity_data.get('notes', '')
        contact_name = activity_data.get('contact_name', 'contact')
        
        prompt = f"""Generate an improved follow-up task based on this activity:

Activity Type: {activity_type}
Contact: {contact_name}
Original Task: {base_task}
Activity Notes: {activity_notes[:200] if activity_notes else 'No notes'}

Provide:
1. Enhanced task title (concise, actionable)
2. Brief description (what needs to be done)
3. Priority (high/medium/low)

Format as JSON:
{{"title": "...", "description": "...", "priority": "medium"}}"""

        try:
            ai_response = self.ai_model.generate(prompt, max_length=250)
            
            # Try to parse JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
            if json_match:
                enhanced = json.loads(json_match.group())
                return {
                    'title': enhanced.get('title', base_task)[:200],
                    'description': enhanced.get('description', '')[:500],
                    'priority': enhanced.get('priority', 'medium')
                }
        except Exception as e:
            print(f"AI enhancement error: {e}")
        
        # Fallback
        return {
            'title': base_task,
            'description': f"Follow up on {activity_type} activity",
            'priority': 'medium'
        }
    
    def generate_smart_reminders(self) -> List[Dict]:
        """
        Generate smart reminders for quiet leads and stalled deals
        
        Returns:
            List of reminders/alerts
        """
        try:
            db = get_db()
            cursor = db.cursor()
            reminders = []
            
            # 1. Quiet leads (no contact in 15+ days)
            cursor.execute('''
                SELECT c.id, c.name,
                       c.company, c.lead_score,
                       MAX(i.created_at) as last_contact
                FROM customers c
                LEFT JOIN interactions i ON c.id = i.customer_id
                WHERE c.status IN ('lead', 'qualified', 'interested')
                  AND c.lead_score > 40
                GROUP BY c.id
                HAVING last_contact IS NULL 
                   OR last_contact < datetime('now', '-15 days')
                ORDER BY c.lead_score DESC
                LIMIT 20
            ''')
            
            quiet_lead_rows = cursor.fetchall()
            
            for row in quiet_lead_rows:
                days_quiet = self._calculate_days_quiet(row[4]) if row[4] else 999
                lead_score = float(row[3]) if row[3] else 0
                
                reminders.append({
                    'type': 'quiet_lead',
                    'priority': 'high' if days_quiet > 30 else 'medium',
                    'contact_id': row[0],
                    'contact_name': row[1],
                    'company': row[2],
                    'lead_score': lead_score,
                    'days_quiet': days_quiet,
                    'message': f"{row[1]} ({row[2] or 'Unknown Company'}) - No contact in {days_quiet} days. Lead score: {lead_score:.1f}",
                    'action': f"Reach out to {row[1]} immediately",
                    'suggested_actions': self._suggest_reengagement_actions(lead_score, days_quiet)
                })
            
            # 2. Stalled deals (no activity in 14+ days)
            cursor.execute('''
                SELECT o.id, o.title, o.stage, o.value,
                       julianday('now') - julianday(o.updated_at) as days_in_stage,
                       c.company,
                       MAX(i.created_at) as last_activity
                FROM opportunities o
                LEFT JOIN customers c ON o.customer_id = c.id
                LEFT JOIN interactions i ON o.customer_id = i.customer_id
                WHERE o.status = 'open' AND o.stage NOT IN ('won', 'lost')
                GROUP BY o.id
                HAVING last_activity IS NULL 
                   OR last_activity < datetime('now', '-14 days')
                ORDER BY o.value DESC NULLS LAST
                LIMIT 15
            ''')
            
            for row in cursor.fetchall():
                days_stalled = self._calculate_days_quiet(row[6]) if row[6] else 999
                value = float(row[3]) if row[3] else 0
                days_in_stage = float(row[4]) if row[4] else 0
                
                # Determine priority based on value and days stalled
                if days_stalled > 30 or (value > 50000 and days_stalled > 20):
                    priority = 'high'
                elif days_stalled > 20 or (value > 20000 and days_stalled > 14):
                    priority = 'medium'
                else:
                    priority = 'low'
                
                reminders.append({
                    'type': 'stalled_deal',
                    'priority': priority,
                    'deal_id': row[0],
                    'deal_title': row[1],
                    'stage': row[2],
                    'value': value,
                    'days_in_stage': days_in_stage,
                    'company': row[5],
                    'days_stalled': days_stalled,
                    'message': f"Deal '{row[1]}' ({row[5] or 'Unknown Company'}) stalled in {row[2]} for {days_stalled} days. Value: ${value:,.0f}",
                    'action': f"Re-engage on '{row[1]}' deal",
                    'suggested_actions': self._suggest_deal_revival_actions(row[2], days_stalled)
                })
            
            # 3. Approaching close dates (within 7 days)
            cursor.execute('''
                SELECT o.id, o.title, o.stage, o.value, o.expected_close_date,
                       c.company,
                       c.name as contact
                FROM opportunities o
                LEFT JOIN customers c ON o.customer_id = c.id
                WHERE o.status = 'open' AND o.stage NOT IN ('won', 'lost')
                  AND o.expected_close_date IS NOT NULL
                  AND o.expected_close_date BETWEEN date('now') AND date('now', '+7 days')
                ORDER BY o.expected_close_date ASC
            ''')
            
            for row in cursor.fetchall():
                try:
                    close_date = datetime.fromisoformat(str(row[4]))
                    days_until = (close_date - datetime.now()).days
                    value = float(row[3]) if row[3] else 0
                    
                    # Determine priority based on urgency and value
                    if days_until <= 2:
                        priority = 'high'
                    elif days_until <= 5 or value > 50000:
                        priority = 'high'
                    else:
                        priority = 'medium'
                    
                    reminders.append({
                        'type': 'closing_soon',
                        'priority': priority,
                        'deal_id': row[0],
                        'deal_title': row[1],
                        'stage': row[2],
                        'value': value,
                        'expected_close_date': row[4],
                        'company': row[5],
                        'contact': row[6],
                        'days_until_close': days_until,
                        'message': f"Deal '{row[1]}' expected to close in {days_until} days (${value:,.0f})",
                        'action': f"Prepare for close: {row[1]}",
                        'suggested_actions': self._suggest_closing_actions(row[2], days_until)
                    })
                except Exception as e:
                    pass  # Silently skip deals with invalid dates
            
            # Sort by priority
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            reminders.sort(key=lambda x: priority_order.get(x['priority'], 3))
            
            return reminders
            
        except Exception as e:
            print(f"Smart reminders error: {e}")
            return []
    
    def _calculate_days_quiet(self, last_contact: str) -> int:
        """Calculate days since last contact"""
        try:
            last_date = datetime.fromisoformat(str(last_contact))
            return (datetime.now() - last_date).days
        except:
            return 999
    
    def _suggest_reengagement_actions(self, lead_score: int, days_quiet: int) -> List[str]:
        """Suggest actions to re-engage quiet leads"""
        actions = []
        
        if lead_score > 70:
            actions.append("📞 Schedule immediate call - high value lead")
            actions.append("📧 Send personalized value proposition email")
        elif lead_score > 40:
            actions.append("📧 Send helpful content or case study")
            actions.append("💡 Share relevant industry insights")
        else:
            actions.append("📧 Add to nurture email campaign")
            actions.append("🔄 Re-qualify lead status")
        
        if days_quiet > 60:
            actions.append("❓ Verify contact information is current")
        
        return actions
    
    def _suggest_deal_revival_actions(self, stage: str, days_stalled: int) -> List[str]:
        """Suggest actions to revive stalled deals"""
        actions = [
            "📞 Schedule check-in call to understand blockers",
            "📝 Send follow-up email with clear next steps"
        ]
        
        if stage == 'Negotiation':
            actions.append("💰 Review pricing and terms")
            actions.append("📋 Provide contract draft")
        elif stage == 'Proposal':
            actions.append("📊 Schedule proposal review meeting")
            actions.append("🎯 Address any outstanding questions")
        elif stage == 'Qualified':
            actions.append("📅 Schedule discovery call or demo")
        
        if days_stalled > 30:
            actions.append("🔄 Re-qualify opportunity")
        
        return actions
    
    def _suggest_closing_actions(self, stage: str, days_until: int) -> List[str]:
        """Suggest actions for deals approaching close date"""
        actions = []
        
        if stage == 'Negotiation':
            actions.append("📋 Finalize contract terms")
            actions.append("🔏 Prepare signature documents")
            actions.append("💼 Coordinate with legal/procurement")
        elif stage in ['Proposal', 'Qualified']:
            actions.append("⚡ Accelerate deal progression")
            actions.append("📞 Schedule urgent meeting")
            actions.append("🎯 Address objections immediately")
        
        if days_until <= 2:
            actions.append("🚨 Immediate action required - closing imminent")
        
        return actions
    
    def enrich_contact_data(self, contact_id: int, auto_save: bool = True) -> Dict:
        """
        Enrich contact data using AI and external sources
        
        Args:
            contact_id: Contact ID to enrich
            auto_save: Whether to automatically save enriched data
        
        Returns:
            Dict with enriched data
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get contact data
            cursor.execute('''
                SELECT c.*
                FROM customers c
                WHERE c.id = ?
            ''', (contact_id,))
            contact_data = dict(cursor.fetchone() or {})
            
            if not contact_data:
                return {'error': 'Contact not found'}
            
            enriched_data = {
                'contact_id': contact_id,
                'original_data': {
                    'name': contact_data.get('name'),
                    'email': contact_data.get('email'),
                    'title': contact_data.get('title'),
                    'company': contact_data.get('company')
                },
                'enriched_data': {},
                'confidence': 0,
                'sources': []
            }
            
            # AI-based title standardization and seniority detection
            if contact_data.get('title'):
                title_analysis = self._analyze_title(contact_data['title'])
                enriched_data['enriched_data']['standardized_title'] = title_analysis['standardized']
                enriched_data['enriched_data']['seniority_level'] = title_analysis['seniority']
                enriched_data['enriched_data']['department'] = title_analysis['department']
                enriched_data['sources'].append('AI Title Analysis')
            
            # Industry insights
            if contact_data.get('industry'):
                industry_insights = self._get_industry_insights(contact_data['industry'])
                enriched_data['enriched_data']['industry_insights'] = industry_insights
                enriched_data['sources'].append('Industry Knowledge Base')
            
            # Company size estimation
            if contact_data.get('company_name'):
                company_insights = self._estimate_company_details(contact_data['company_name'])
                enriched_data['enriched_data']['estimated_company_size'] = company_insights['size']
                enriched_data['enriched_data']['estimated_revenue_range'] = company_insights['revenue']
                enriched_data['sources'].append('AI Company Analysis')
            
            # Calculate confidence score
            enriched_data['confidence'] = self._calculate_enrichment_confidence(enriched_data)
            
            # Auto-save if requested
            if auto_save and enriched_data['enriched_data']:
                self._save_enriched_data(cursor, contact_id, enriched_data)
                db.commit()
            
            enriched_data['timestamp'] = datetime.now().isoformat()
            enriched_data['success'] = True
            
            return enriched_data
            
        except Exception as e:
            print(f"Data enrichment error: {e}")
            return {'error': str(e)}
    
    def _analyze_title(self, title: str) -> Dict:
        """Analyze job title to extract insights"""
        prompt = f"""Analyze this job title: "{title}"

Provide:
1. Standardized title (e.g., "VP of Sales" → "Vice President of Sales")
2. Seniority level (C-Level/VP/Director/Manager/Individual Contributor)
3. Department (Sales/Marketing/Engineering/Operations/Finance/HR/Other)

Format as JSON:
{{"standardized": "...", "seniority": "...", "department": "..."}}"""

        try:
            ai_response = self.ai_model.generate(prompt, max_length=150)
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                return result
        except Exception as e:
            print(f"Title analysis error: {e}")
        
        # Fallback
        return {
            'standardized': title,
            'seniority': 'Unknown',
            'department': 'Unknown'
        }
    
    def _get_industry_insights(self, industry: str) -> Dict:
        """Get insights about specific industry"""
        insights = {
            'technology': {
                'avg_deal_cycle': '60-90 days',
                'key_concerns': 'Scalability, security, ROI',
                'decision_makers': 'CTO, VP Engineering'
            },
            'finance': {
                'avg_deal_cycle': '90-180 days',
                'key_concerns': 'Compliance, security, reliability',
                'decision_makers': 'CFO, Head of Operations'
            },
            'healthcare': {
                'avg_deal_cycle': '120-180 days',
                'key_concerns': 'HIPAA compliance, data security',
                'decision_makers': 'CIO, Head of IT'
            },
            'retail': {
                'avg_deal_cycle': '30-60 days',
                'key_concerns': 'Cost, ease of use, integration',
                'decision_makers': 'COO, Director of Operations'
            }
        }
        
        return insights.get(industry.lower(), {
            'avg_deal_cycle': '60-90 days',
            'key_concerns': 'Value, reliability, support',
            'decision_makers': 'Executive team'
        })
    
    def _estimate_company_details(self, company_name: str) -> Dict:
        """Estimate company size and revenue using AI"""
        prompt = f"""Estimate details for company: "{company_name}"

Provide educated guess for:
1. Company size category (Startup/Small/Medium/Enterprise/Unknown)
2. Estimated annual revenue range

Format as JSON:
{{"size": "...", "revenue": "..."}}"""

        try:
            ai_response = self.ai_model.generate(prompt, max_length=100)
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
            
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        return {
            'size': 'Unknown',
            'revenue': 'Unknown'
        }
    
    def _calculate_enrichment_confidence(self, enriched_data: Dict) -> float:
        """Calculate confidence score for enriched data"""
        confidence = 50.0
        
        enriched_fields = enriched_data.get('enriched_data', {})
        
        # More enriched fields = higher confidence
        confidence += len(enriched_fields) * 10
        
        # Adjust based on sources
        confidence += len(enriched_data.get('sources', [])) * 5
        
        return min(100.0, confidence)
    
    def _save_enriched_data(self, cursor, contact_id: int, enriched_data: Dict):
        """Save enriched data to database"""
        enriched = enriched_data.get('enriched_data', {})
        
        # Update contact with enriched data (store in custom_fields as JSON)
        update_fields = {}
        
        if 'seniority_level' in enriched:
            # Could add seniority_level column or store in notes
            update_fields['notes'] = f"Seniority: {enriched['seniority_level']}"
        
        # For now, we'll store enriched data in a JSON field if it exists
        # In production, you might want to add specific columns
        
        cursor.execute('''
            UPDATE contacts 
            SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (contact_id,))
    
    def auto_log_activity(self, activity_type: str, contact_id: int = None, 
                         company_id: int = None, deal_id: int = None, 
                         notes: str = "") -> Dict:
        """
        Auto-log email, call, or meeting activity
        
        Args:
            activity_type: Type of activity (email/call/meeting)
            contact_id: Associated contact
            company_id: Associated company
            deal_id: Associated deal
            notes: Activity notes
        
        Returns:
            Dict with activity_id and generated tasks
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Create activity
            cursor.execute('''
                INSERT INTO activities (type, contact_id, company_id, deal_id, notes, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (activity_type, contact_id, company_id, deal_id, notes))
            
            activity_id = cursor.lastrowid
            db.commit()
            
            # Auto-generate follow-up task
            task_result = self.auto_generate_follow_up_tasks(activity_id)
            
            return {
                'success': True,
                'activity_id': activity_id,
                'follow_up_task': task_result,
                'message': f"Logged {activity_type} activity and created follow-up task"
            }
            
        except Exception as e:
            print(f"Auto-log activity error: {e}")
            return {'error': str(e)}
