"""
AI Actions Module - CRM Operations via Chatbot
Handles adding companies, contacts, logging interactions, creating deals, and managing tasks
"""

import sqlite3
from datetime import datetime, timedelta
import re
from typing import Dict, List, Optional, Any
from modules import db_helper
from modules.groq_ai import GroqAI

class AIActions:
    def __init__(self):
        self.groq_ai = GroqAI()
    
    def add_company(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Add a new company to the CRM"""
        try:
            db = db_helper.get_db()
            cursor = db.cursor()
            
            # Check if company already exists
            cursor.execute("SELECT id FROM companies WHERE name = ?", (data['name'],))
            existing = cursor.fetchone()
            
            if existing:
                return {
                    'success': False,
                    'message': f"Company '{data['name']}' already exists.",
                    'company_id': existing[0]
                }
            
            # Insert company
            cursor.execute("""
                INSERT INTO companies (name, industry, size, revenue, website, phone, 
                                     email, address, city, state, country, description, 
                                     assigned_to, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
            """, (
                data['name'],
                data.get('industry'),
                data.get('size'),
                data.get('revenue'),
                data.get('website'),
                data.get('phone'),
                data.get('email'),
                data.get('address'),
                data.get('city'),
                data.get('state'),
                data.get('country'),
                data.get('description'),
                user_id
            ))
            
            company_id = cursor.lastrowid
            db.commit()
            
            return {
                'success': True,
                'message': f"✅ Company '{data['name']}' added successfully!",
                'company_id': company_id,
                'navigation_target': '/customers'
            }
            
        except Exception as e:
            print(f"Error adding company: {e}")
            return {
                'success': False,
                'message': f"Failed to add company: {str(e)}"
            }
    
    def add_contact(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Add a new contact/customer to the CRM"""
        try:
            db = db_helper.get_db()
            cursor = db.cursor()
            
            # Check if contact already exists by email
            if data.get('email'):
                cursor.execute("SELECT id FROM customers WHERE email = ?", (data['email'],))
                existing = cursor.fetchone()
                
                if existing:
                    return {
                        'success': False,
                        'message': f"Contact with email '{data['email']}' already exists.",
                        'contact_id': existing[0]
                    }
            
            # Get or create company
            company_id = None
            if data.get('company'):
                cursor.execute("SELECT id FROM companies WHERE name = ?", (data['company'],))
                company = cursor.fetchone()
                if company:
                    company_id = company[0]
            
            # Insert contact
            cursor.execute("""
                INSERT INTO customers (name, email, phone, company, industry, status, 
                                     budget, location, website, notes, assigned_to, 
                                     company_id, job_title, source, linkedin_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['name'],
                data.get('email'),
                data.get('phone'),
                data.get('company'),
                data.get('industry'),
                data.get('status', 'lead'),
                data.get('budget'),
                data.get('location'),
                data.get('website'),
                data.get('notes'),
                user_id,
                company_id,
                data.get('job_title'),
                data.get('source'),
                data.get('linkedin_url')
            ))
            
            contact_id = cursor.lastrowid
            db.commit()
            
            return {
                'success': True,
                'message': f"✅ Contact '{data['name']}' added successfully!",
                'contact_id': contact_id,
                'navigation_target': '/customers'
            }
            
        except Exception as e:
            print(f"Error adding contact: {e}")
            return {
                'success': False,
                'message': f"Failed to add contact: {str(e)}"
            }
    
    def log_interaction(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Log a customer interaction (call, email, meeting)"""
        try:
            db = db_helper.get_db()
            cursor = db.cursor()
            
            # Verify customer exists
            cursor.execute("SELECT id, name FROM customers WHERE id = ?", (data['customer_id'],))
            customer = cursor.fetchone()
            
            if not customer:
                return {
                    'success': False,
                    'message': f"Customer with ID {data['customer_id']} not found."
                }
            
            # Insert interaction
            cursor.execute("""
                INSERT INTO interactions (customer_id, user_id, type, channel, subject, 
                                        notes, outcome, next_action)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data['customer_id'],
                user_id,
                data['type'],
                data.get('channel'),
                data.get('subject'),
                data.get('notes'),
                data.get('outcome'),
                data.get('next_action')
            ))
            
            interaction_id = cursor.lastrowid
            
            # Update customer's updated_at timestamp
            cursor.execute("""
                UPDATE customers 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (data['customer_id'],))
            
            db.commit()
            
            # Auto-generate follow-up task if needed
            task_result = None
            if data.get('auto_followup', True):
                task_result = self._auto_generate_followup_task(
                    customer_id=data['customer_id'],
                    interaction_type=data['type'],
                    notes=data.get('notes', ''),
                    user_id=user_id
                )
            
            return {
                'success': True,
                'message': f"✅ {data['type'].capitalize()} logged for {customer[1]}!",
                'interaction_id': interaction_id,
                'followup_task': task_result,
                'navigation_target': '/interactions'
            }
            
        except Exception as e:
            print(f"Error logging interaction: {e}")
            return {
                'success': False,
                'message': f"Failed to log interaction: {str(e)}"
            }
    
    def create_deal(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a new deal/opportunity"""
        try:
            db = db_helper.get_db()
            cursor = db.cursor()
            
            # Verify customer exists
            cursor.execute("SELECT id, name FROM customers WHERE id = ?", (data['customer_id'],))
            customer = cursor.fetchone()
            
            if not customer:
                return {
                    'success': False,
                    'message': f"Customer with ID {data['customer_id']} not found."
                }
            
            # Get company_id if available
            cursor.execute("SELECT company_id FROM customers WHERE id = ?", (data['customer_id'],))
            result = cursor.fetchone()
            company_id = result[0] if result and result[0] else None
            
            # Insert opportunity
            cursor.execute("""
                INSERT INTO opportunities (customer_id, title, value, probability, stage, 
                                         expected_close_date, status, notes, deal_stage, 
                                         deal_type, deal_source, company_id)
                VALUES (?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?, ?)
            """, (
                data['customer_id'],
                data['title'],
                data.get('value', 0),
                data.get('probability', 0.5),
                data.get('stage', 'prospecting'),
                data.get('expected_close_date'),
                data.get('notes'),
                data.get('deal_stage', 'Lead'),
                data.get('deal_type'),
                data.get('deal_source'),
                company_id
            ))
            
            deal_id = cursor.lastrowid
            db.commit()
            
            return {
                'success': True,
                'message': f"✅ Deal '{data['title']}' created for {customer[1]}!",
                'deal_id': deal_id,
                'navigation_target': '/pipeline'
            }
            
        except Exception as e:
            print(f"Error creating deal: {e}")
            return {
                'success': False,
                'message': f"Failed to create deal: {str(e)}"
            }
    
    def create_task(self, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create a task or reminder"""
        try:
            db = db_helper.get_db()
            cursor = db.cursor()
            
            # Verify customer exists if customer_id provided
            if data.get('customer_id'):
                cursor.execute("SELECT id FROM customers WHERE id = ?", (data['customer_id'],))
                if not cursor.fetchone():
                    return {
                        'success': False,
                        'message': f"Customer with ID {data['customer_id']} not found."
                    }
            
            # Calculate due date if not provided
            due_date = data.get('due_date')
            if not due_date and data.get('days_from_now'):
                due_date = (datetime.now() + timedelta(days=data['days_from_now'])).isoformat()
            
            # Insert task
            cursor.execute("""
                INSERT INTO tasks (customer_id, user_id, title, description, due_date, 
                                 priority, status, type, category, notes, assigned_to)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?)
            """, (
                data.get('customer_id'),
                user_id,
                data['title'],
                data.get('description'),
                due_date,
                data.get('priority', 'medium'),
                data.get('type', 'follow-up'),
                data.get('category'),
                data.get('notes'),
                data.get('assigned_to', user_id)
            ))
            
            task_id = cursor.lastrowid
            db.commit()
            
            return {
                'success': True,
                'message': f"✅ Task '{data['title']}' created!",
                'task_id': task_id
            }
            
        except Exception as e:
            print(f"Error creating task: {e}")
            return {
                'success': False,
                'message': f"Failed to create task: {str(e)}"
            }
    
    def _auto_generate_followup_task(self, customer_id: int, interaction_type: str, 
                                    notes: str, user_id: int) -> Optional[Dict[str, Any]]:
        """Auto-generate intelligent follow-up task after interaction"""
        try:
            # Use AI to determine if follow-up is needed and when
            prompt = f"""
Based on this {interaction_type} interaction:
{notes[:500]}

Determine:
1. Is a follow-up needed? (yes/no)
2. When should the follow-up occur? (1-7 days from now)
3. What should the follow-up action be? (short description)
4. Priority level? (low/medium/high)

Respond in this exact format:
FOLLOWUP: yes/no
DAYS: number
ACTION: description
PRIORITY: low/medium/high
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=200)
            
            # Parse AI response
            followup_needed = 'yes' in response.lower().split('followup:')[1].split('\n')[0].lower() if 'followup:' in response.lower() else False
            
            if not followup_needed:
                return None
            
            # Extract details
            days = 3  # default
            action = "Follow up on recent interaction"
            priority = "medium"
            
            if 'days:' in response.lower():
                try:
                    days_str = response.lower().split('days:')[1].split('\n')[0].strip()
                    days = int(re.search(r'\d+', days_str).group())
                except:
                    pass
            
            if 'action:' in response.lower():
                action = response.split('ACTION:')[1].split('\n')[0].strip()
            
            if 'priority:' in response.lower():
                priority_line = response.lower().split('priority:')[1].split('\n')[0].strip()
                if 'high' in priority_line:
                    priority = 'high'
                elif 'low' in priority_line:
                    priority = 'low'
            
            # Create the task
            task_data = {
                'customer_id': customer_id,
                'title': f"Follow-up: {interaction_type}",
                'description': action,
                'days_from_now': days,
                'priority': priority,
                'type': 'follow-up'
            }
            
            return self.create_task(task_data, user_id)
            
        except Exception as e:
            print(f"Error auto-generating follow-up: {e}")
            return None
    
    def parse_natural_language_action(self, message: str) -> Dict[str, Any]:
        """Parse natural language to extract action details using AI"""
        try:
            prompt = f"""
Extract structured data from this CRM action request:
"{message}"

Identify the action type and extract all relevant details.

Respond in JSON format:
{{
    "action": "add_contact|add_company|log_interaction|create_deal|create_task",
    "data": {{
        // relevant fields based on action type
    }}
}}

For add_contact, include: name, email, phone, company, job_title, location, notes
For add_company, include: name, industry, website, phone, email, description
For log_interaction, include: customer_id/customer_name, type (call/email/meeting), notes, outcome
For create_deal, include: customer_id/customer_name, title, value, stage, expected_close_date
For create_task, include: title, description, due_date, priority, customer_id/customer_name
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=500)
            
            # Try to parse JSON from response
            import json
            # Extract JSON from response (might be wrapped in markdown)
            json_match = re.search(r'```json\n(.*?)\n```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                json_str = json_match.group(0) if json_match else response
            
            parsed = json.loads(json_str)
            return parsed
            
        except Exception as e:
            print(f"Error parsing natural language: {e}")
            return {
                'action': 'unknown',
                'data': {},
                'error': str(e)
            }
    
    def execute_action(self, action_type: str, data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Execute a CRM action based on type"""
        action_map = {
            'add_contact': self.add_contact,
            'add_company': self.add_company,
            'log_interaction': self.log_interaction,
            'create_deal': self.create_deal,
            'create_task': self.create_task
        }
        
        action_func = action_map.get(action_type)
        if not action_func:
            return {
                'success': False,
                'error': f'Unknown action type: {action_type}',
                'available_actions': list(action_map.keys())
            }
        
        try:
            return action_func(data, user_id)
        except Exception as e:
            import traceback
            print(f"Error executing {action_type}: {e}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }
    
    def auto_generate_tasks(self, interaction_type: str, customer_id: int, 
                           deal_id: Optional[int] = None, notes: str = "", 
                           user_id: int = 1) -> List[Dict[str, Any]]:
        """Auto-generate follow-up tasks based on interaction"""
        tasks = []
        
        try:
            db = db_helper.get_db()
            cursor = db.cursor()
            
            # Get customer info
            cursor.execute("SELECT name FROM customers WHERE id = ?", (customer_id,))
            customer = cursor.fetchone()
            if not customer:
                return tasks
            
            customer_name = customer[0]
            
            # Use AI to generate intelligent task suggestions
            prompt = f"""
Based on this CRM interaction, suggest 2-3 specific follow-up tasks:

Interaction Type: {interaction_type}
Customer: {customer_name}
Notes: {notes}

Generate practical, actionable tasks with:
1. Clear title
2. Brief description
3. Suggested due date (in days from now)
4. Priority (low/medium/high)

Respond in JSON format:
[
  {{
    "title": "...",
    "description": "...",
    "due_in_days": 3,
    "priority": "medium"
  }}
]
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=500)
            
            # Parse AI response
            import json
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                suggested_tasks = json.loads(json_match.group(0))
                
                # Create tasks in database
                for task_data in suggested_tasks:
                    due_date = (datetime.now() + timedelta(days=task_data.get('due_in_days', 3))).strftime('%Y-%m-%d')
                    
                    cursor.execute("""
                        INSERT INTO tasks (title, description, due_date, priority, status, 
                                         customer_id, deal_id, assigned_to, created_at)
                        VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?)
                    """, (
                        task_data['title'],
                        task_data.get('description', ''),
                        due_date,
                        task_data.get('priority', 'medium'),
                        customer_id,
                        deal_id,
                        user_id,
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    
                    task_id = cursor.lastrowid
                    db.commit()
                    
                    tasks.append({
                        'id': task_id,
                        'title': task_data['title'],
                        'description': task_data.get('description'),
                        'due_date': due_date,
                        'priority': task_data.get('priority', 'medium')
                    })
            
            return tasks
            
        except Exception as e:
            import traceback
            print(f"Error auto-generating tasks: {e}")
            print(traceback.format_exc())
            return tasks
