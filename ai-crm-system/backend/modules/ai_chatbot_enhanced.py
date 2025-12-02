"""
Enhanced AI Chatbot Module - CRM Data Query & Navigation
Allows users to query CRM data, navigate to sections, and perform actions via natural language
"""

import json
import re
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .groq_ai import GroqAI
from .db_helper import get_db

class EnhancedChatbot:
    def __init__(self, ai_model: GroqAI):
        """Initialize enhanced chatbot with CRM query capabilities"""
        self.ai_model = ai_model
        
        # Import action modules
        try:
            from .ai_actions import AIActions
            from .email_automation import EmailAutomation
            from .data_enrichment import DataEnrichment
            self.actions = AIActions()
            self.email_automation = EmailAutomation()
            self.data_enrichment = DataEnrichment()
        except ImportError as e:
            print(f"Warning: Could not import automation modules: {e}")
            self.actions = None
            self.email_automation = None
            self.data_enrichment = None
        
        # Navigation map for CRM sections
        self.navigation_map = {
            'dashboard': '/dashboard',
            'companies': '/companies',
            'contacts': '/contacts',
            'deals': '/deals',
            'pipeline': '/pipeline',
            'reports': '/reports',
            'settings': '/settings',
            'interactions': '/interactions',
            'tasks': '/tasks',
            'activities': '/activities'
        }
        
        # Query patterns for CRM data
        self.query_patterns = {
            'leads': ['leads', 'prospects', 'potential customers'],
            'deals': ['deals', 'opportunities', 'sales'],
            'contacts': ['contacts', 'people', 'persons'],
            'companies': ['companies', 'organizations', 'businesses'],
            'activities': ['activities', 'interactions', 'touchpoints'],
            'tasks': ['tasks', 'todos', 'to-dos', 'action items'],
            'won': ['closed won', 'won deals', 'successful deals'],
            'lost': ['closed lost', 'lost deals', 'failed deals'],
            'summary': ['summarize', 'summary', 'overview', 'all information', 'everything', 'full report']
        }
    
    def process_query(self, message: str, user_context: Dict = None) -> Dict:
        """
        Process natural language query and return structured response
        
        Args:
            message: User's natural language query
            user_context: Optional user context (permissions, filters, etc.)
        
        Returns:
            Dict with intent, data, navigation_target, and response message
        """
        message_lower = message.lower().strip()
        
        # Detect intent using AI
        intent_result = self._detect_intent(message)
        intent = intent_result.get('intent')
        
        response = {
            'intent': intent,
            'data': None,
            'navigation_target': None,
            'message': '',
            'actions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        # Handle different intents
        if intent == 'query_data':
            response = self._handle_data_query(message, intent_result)
        elif intent == 'navigate':
            response = self._handle_navigation(message)
        elif intent == 'create_record':
            response = self._handle_create_action(message, intent_result)
        elif intent == 'delete_record':
            response = self._handle_delete_action(message, intent_result)
        elif intent == 'update_record':
            response = self._handle_update_action(message, intent_result)
        elif intent == 'analytics':
            response = self._handle_analytics_query(message)
        elif intent == 'draft_email':
            response = self._handle_email_drafting(message)
        elif intent == 'send_email':
            response = self._handle_send_email(message)
        elif intent == 'sync_emails':
            response = self._handle_email_sync(message)
        elif intent == 'enrich_data':
            response = self._handle_data_enrichment(message)
        elif intent == 'analyze_sentiment':
            response = self._handle_sentiment_analysis(message)
        else:
            response['message'] = self._generate_ai_response(message)
        
        return response
    
    def _detect_intent(self, message: str) -> Dict:
        """Detect user intent using AI and patterns"""
        message_lower = message.lower()
        
        # Email operations - HIGHEST PRIORITY (check FIRST before everything)
        if any(word in message_lower for word in ['send email', 'email to', 'send to']):
            return {'intent': 'send_email', 'confidence': 0.95}
        
        if any(word in message_lower for word in ['draft', 'write', 'compose']) and 'email' in message_lower:
            return {'intent': 'draft_email', 'confidence': 0.95}
        
        if any(word in message_lower for word in ['sync email', 'check email', 'get email', 'fetch email']):
            return {'intent': 'sync_emails', 'confidence': 0.9}
        
        # Navigation patterns - enhanced
        navigation_keywords = ['go to', 'take me to', 'open', 'navigate to', 'navigate', 
                             'show me the', 'go back to', 'return to', 'switch to']
        if any(word in message_lower for word in navigation_keywords):
            return {'intent': 'navigate', 'confidence': 0.95}
        
        # Create/Add actions - high priority
        if any(word in message_lower for word in ['create', 'add', 'new', 'register']):
            return {'intent': 'create_record', 'confidence': 0.9}
        
        # Pattern: "Company Acme" or "Contact John" (entity name pattern) - treat as creation
        words = message.split()
        if (len(words) >= 2 and 
            words[0].lower() in ['company', 'contact', 'deal', 'task', 'opportunity'] and 
            words[1][0].isupper()):
            return {'intent': 'create_record', 'confidence': 0.85}
        
        # Log actions (interactions)
        if any(word in message_lower for word in ['log interaction', 'log call', 'log email', 'log meeting', 'record interaction']):
            return {'intent': 'create_record', 'confidence': 0.9}
        
        # Update actions (pipeline stages, task status, etc.)
        if any(word in message_lower for word in ['move', 'change', 'update', 'modify', 'set', 'mark', 'complete']):
            return {'intent': 'update_record', 'confidence': 0.9}
        
        # Delete actions
        if any(word in message_lower for word in ['delete', 'remove', 'drop']):
            return {'intent': 'delete_record', 'confidence': 0.9}
        
        # CRM Summary - check before general query patterns
        summary_keywords = ['summarize', 'summary', 'overview', 'all information', 
                           'everything', 'full report', 'complete data', 'entire crm']
        if any(word in message_lower for word in summary_keywords):
            return {'intent': 'query_data', 'confidence': 0.95}
        
        # Data query patterns - enhanced
        query_keywords = ['show', 'list', 'find', 'get', 'display', 'what are', 
                         'give me', 'tell me', 'see', 'view', 'search', 'recent', 'latest']
        if any(word in message_lower for word in query_keywords):
            if any(word in message_lower for word in ['how many', 'count', 'total', 'sum']):
                return {'intent': 'analytics', 'confidence': 0.9}
            return {'intent': 'query_data', 'confidence': 0.9}
        
        # Implicit queries with time/quality modifiers
        time_quality_words = ['this week', 'closing', 'won', 'lost', 'today', 'yesterday', 'month', 'recent', 'latest', 'top', 'best', 'new']
        data_types = ['deals', 'opportunities', 'contacts', 'leads', 'customers', 'companies']
        
        has_data_type = any(word in message_lower for word in data_types)
        has_modifier = any(word in message_lower for word in time_quality_words)
        
        if has_data_type and has_modifier:
            return {'intent': 'query_data', 'confidence': 0.85}
        
        # Question patterns
        if any(message_lower.startswith(q) for q in ['what', 'which', 'who', 'how many']):
            if has_data_type:
                return {'intent': 'query_data', 'confidence': 0.8}
        
        # Update actions
        if any(word in message_lower for word in ['update', 'change', 'modify', 'edit']):
            return {'intent': 'update_record', 'confidence': 0.8}
        
        # Email syncing
        if any(word in message_lower for word in ['sync email', 'check email', 'get email', 'fetch email']):
            return {'intent': 'sync_emails', 'confidence': 0.9}
        
        # Data enrichment
        if any(word in message_lower for word in ['enrich', 'lookup', 'find info about']):
            return {'intent': 'enrich_data', 'confidence': 0.9}
        
        # Sentiment analysis
        if 'sentiment' in message_lower or 'analyze this message' in message_lower:
            return {'intent': 'analyze_sentiment', 'confidence': 0.9}
        
        # Use AI for complex intent detection
        prompt = f"""Analyze this CRM user query and determine the intent.

User query: "{message}"

Possible intents:
- query_data: User wants to see/find CRM data
- navigate: User wants to go to a specific section
- create_record: User wants to add new record
- update_record: User wants to modify existing record
- analytics: User wants statistics or analysis
- general: General question or conversation

Respond with ONLY ONE WORD (the intent)."""

        try:
            ai_intent = self.ai_model.generate(prompt, max_length=20).strip().lower()
            valid_intents = ['query_data', 'navigate', 'create_record', 'update_record', 'analytics', 'general']
            
            for valid in valid_intents:
                if valid in ai_intent:
                    return {'intent': valid, 'confidence': 0.7}
        except:
            pass
        
        return {'intent': 'general', 'confidence': 0.5}
    
    def _handle_data_query(self, message: str, intent_result: Dict) -> Dict:
        """Handle CRM data queries"""
        message_lower = message.lower()
        response = {
            'intent': 'query_data',
            'data': None,
            'navigation_target': None,
            'message': '',
            'actions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Detect what data user wants
            if any(word in message_lower for word in self.query_patterns['leads']):
                response['data'] = self._query_leads(cursor, message) or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Found {count} lead{'s' if count != 1 else ''}:\n\n"
                    for i, lead in enumerate(response['data'][:5], 1):
                        response['message'] += f"{i}. {lead.get('name', 'N/A')} - {lead.get('company_name', 'No company')} (Score: {lead.get('lead_score', 0)})\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No leads found matching your criteria."
                response['navigation_target'] = None  # Don't auto-navigate, just show data
            
            elif any(word in message_lower for word in self.query_patterns['deals']):
                response['data'] = self._query_deals(cursor, message) or []
                count = len(response['data'])
                if count > 0:
                    total_value = sum(d.get('value', 0) or 0 for d in response['data'])
                    response['message'] = f"Found {count} deal{'s' if count != 1 else ''} (Total value: ${total_value:,.2f}):\n\n"
                    for i, deal in enumerate(response['data'][:5], 1):
                        value_str = f"${deal.get('value', 0):,.0f}" if deal.get('value') else "No value"
                        close_date = deal.get('expected_close_date', 'No date')
                        response['message'] += f"{i}. {deal.get('title', 'N/A')} - {value_str} (Close: {close_date})\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No deals found matching your criteria."
                response['navigation_target'] = None  # Don't auto-navigate, just show data
            
            elif any(word in message_lower for word in self.query_patterns['companies']):
                response['data'] = self._query_companies(cursor, message) or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Found {count} compan{'y' if count == 1 else 'ies'}:\n\n"
                    for i, company in enumerate(response['data'][:5], 1):
                        revenue = company.get('total_revenue', 0) or 0
                        response['message'] += f"{i}. {company.get('name', 'N/A')} - ${revenue:,.0f} revenue\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No companies found."
                response['navigation_target'] = None  # Don't auto-navigate
            
            elif any(word in message_lower for word in self.query_patterns['contacts']):
                response['data'] = self._query_contacts(cursor, message) or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Found {count} contact{'s' if count != 1 else ''}:\n\n"
                    for i, contact in enumerate(response['data'][:5], 1):
                        title = contact.get('title') or contact.get('job_title') or 'No title'
                        company = contact.get('company_name') or contact.get('company') or 'No company'
                        response['message'] += f"{i}. {contact.get('name', 'N/A')} - {title} at {company}\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No contacts found. Try: 'show contacts' or add some in the Contacts page."
                response['navigation_target'] = None  # Don't auto-navigate
            
            elif any(word in message_lower for word in self.query_patterns['won']):
                response['data'] = self._query_deals(cursor, message, stage='won') or []
                count = len(response['data'])
                if count > 0:
                    total_value = sum(d.get('value', 0) or 0 for d in response['data'])
                    response['message'] = f"Found {count} won deal{'s' if count != 1 else ''} (Total: ${total_value:,.2f}):\n\n"
                    for i, deal in enumerate(response['data'][:5], 1):
                        value_str = f"${deal.get('value', 0):,.0f}" if deal.get('value') else "No value"
                        response['message'] += f"{i}. {deal.get('title', 'N/A')} - {value_str}\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No won deals found. Try creating some deals in the Pipeline!"
                response['navigation_target'] = None  # Don't auto-navigate
            
            elif any(word in message_lower for word in self.query_patterns['lost']):
                response['data'] = self._query_deals(cursor, message, stage='lost') or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Found {count} lost deal{'s' if count != 1 else ''}:\n\n"
                    for i, deal in enumerate(response['data'][:5], 1):
                        value_str = f"${deal.get('value', 0):,.0f}" if deal.get('value') else "No value"
                        response['message'] += f"{i}. {deal.get('title', 'N/A')} - {value_str}\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No lost deals found."
                response['navigation_target'] = None  # Don't auto-navigate
            
            # Recent interactions
            elif any(word in message_lower for word in ['recent', 'latest', 'last']) and any(word in message_lower for word in ['interaction', 'activity', 'touchpoint']):
                response['data'] = self._query_recent_interactions(cursor, message) or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Found {count} recent interaction{'s' if count != 1 else ''}:\n\n"
                    for i, interaction in enumerate(response['data'][:5], 1):
                        response['message'] += f"{i}. {interaction.get('type', 'N/A')} with {interaction.get('customer_name', 'Unknown')}\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No recent interactions found."
                response['navigation_target'] = None  # Don't auto-navigate
            
            # Stalled deals
            elif 'stalled' in message_lower or 'stuck' in message_lower:
                response['data'] = self._query_stalled_deals(cursor) or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Found {count} stalled deal{'s' if count != 1 else ''} needing attention:\n\n"
                    for i, deal in enumerate(response['data'][:5], 1):
                        days = int(deal.get('days_stalled', 0))
                        response['message'] += f"{i}. {deal.get('title', 'N/A')} - Stalled for {days} days\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No stalled deals found."
                response['navigation_target'] = None  # Don't auto-navigate
            
            # Tasks query
            elif any(word in message_lower for word in self.query_patterns['tasks']):
                response['data'] = self._query_tasks(cursor, message) or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Found {count} task{'s' if count != 1 else ''}:\n\n"
                    for i, task in enumerate(response['data'][:5], 1):
                        status = task.get('status', 'N/A')
                        priority = task.get('priority', 'N/A')
                        response['message'] += f"{i}. {task.get('title', 'N/A')} - Status: {status}, Priority: {priority}\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No tasks found."
                response['navigation_target'] = None
            
            # CRM Summary - comprehensive overview
            elif any(word in message_lower for word in self.query_patterns['summary']):
                response = self._handle_crm_summary(cursor, message)
            
            # Top customers
            elif 'top' in message_lower and ('customer' in message_lower or 'client' in message_lower):
                response['data'] = self._query_top_customers(cursor) or []
                count = len(response['data'])
                if count > 0:
                    response['message'] = f"Here are your top {count} customer{'s' if count != 1 else ''}:\n\n"
                    for i, customer in enumerate(response['data'][:5], 1):
                        revenue = customer.get('total_revenue', 0) or 0
                        response['message'] += f"{i}. {customer.get('name', 'N/A')} - ${revenue:,.0f} revenue\n"
                    if count > 5:
                        response['message'] += f"\n...and {count - 5} more."
                else:
                    response['message'] = "No top customers found."
                response['navigation_target'] = None  # Don't auto-navigate
            
            else:
                # Use AI to understand the query
                response['data'] = self._ai_assisted_query(cursor, message) or []
                response['message'] = "Here's what I found based on your query."
            
        except Exception as e:
            import traceback
            print(f"Query error: {e}")
            print(traceback.format_exc())
            
            # Provide helpful error message based on query type
            if 'deal' in message_lower or 'opportunit' in message_lower:
                response['message'] = "I couldn't find any deals matching your criteria. Try asking 'show deals' or 'show closing deals this week'."
            elif 'lead' in message_lower:
                response['message'] = "I couldn't find any leads. Try asking 'show top leads' or 'show recent leads'."
            elif 'contact' in message_lower:
                response['message'] = "I couldn't find any contacts. Try asking 'show contacts' or 'show recent contacts'."
            else:
                response['message'] = "I encountered an error processing your query. Try using clear action words like 'show deals' or 'list contacts'."
            response['data'] = []
        
        return response
    
    def _query_leads(self, cursor, message: str) -> List[Dict]:
        """Query leads based on natural language"""
        # Extract time filters
        days_back = self._extract_time_period(message)
        
        # Extract source filter
        source = self._extract_source(message)
        
        # Build query
        query = '''
            SELECT c.id, c.name, c.email, c.job_title as title,
                   c.company as company_name, c.lead_score, c.status, c.created_at
            FROM customers c
            WHERE 1=1
        '''
        params = []
        
        # Add status filter for leads (or any customer with a lead_score)
        query += " AND (c.status IN ('lead', 'qualified', 'interested') OR c.status IS NULL OR c.lead_score > 0)"
        
        if days_back:
            query += " AND c.created_at >= datetime('now', '-{} days')".format(days_back)
        
        if source:
            query += " AND LOWER(c.lead_source) LIKE ?"
            params.append(f'%{source}%')
        
        # Check for score filter
        if 'high score' in message.lower() or 'top' in message.lower():
            query += " AND c.lead_score > 70"
        
        query += " ORDER BY c.lead_score DESC, c.created_at DESC LIMIT 50"
        
        try:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Leads query error: {e}")
            return []
    
    def _query_deals(self, cursor, message: str, stage: str = None) -> List[Dict]:
        """Query deals based on natural language"""
        message_lower = message.lower()
        days_back = self._extract_time_period(message)
        
        query = '''
            SELECT o.id, o.title, o.value, o.stage,
                   o.expected_close_date, o.updated_at as last_updated,
                   c.company as company_name,
                   c.name as primary_contact,
                   o.status
            FROM opportunities o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE 1=1
        '''
        params = []
        
        # Check for "closing this week" or "closing soon"
        if 'closing' in message_lower and any(word in message_lower for word in ['week', 'soon', '7 days', 'this week']):
            query += " AND o.status = 'open'"
            query += " AND o.expected_close_date IS NOT NULL"
            query += " AND o.expected_close_date BETWEEN date('now') AND date('now', '+7 days')"
            query += " ORDER BY o.expected_close_date ASC, o.value DESC LIMIT 50"
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        
        # Check for time-based filters
        if 'today' in message_lower:
            query += " AND date(o.expected_close_date) = date('now')"
        elif 'this month' in message_lower:
            query += " AND strftime('%Y-%m', o.expected_close_date) = strftime('%Y-%m', 'now')"
        elif days_back:
            query += " AND o.created_at >= datetime('now', '-{} days')".format(days_back)
        
        # Status filters
        if stage:
            query += " AND o.stage = ?"
            params.append(stage)
        elif 'won' in message_lower or 'closed won' in message_lower:
            query += " AND o.stage = 'won'"
        elif 'lost' in message_lower or 'closed lost' in message_lower:
            query += " AND o.stage = 'lost'"
        else:
            query += " AND o.status = 'open'"
        
        # Check for value filters
        if 'large' in message_lower or 'big' in message_lower:
            query += " AND o.value > 50000"
        elif 'small' in message_lower:
            query += " AND o.value < 10000"
        
        query += " ORDER BY o.value DESC, o.created_at DESC LIMIT 50"
        
        try:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Deals query error: {e}")
            return []
    
    def _query_companies(self, cursor, message: str) -> List[Dict]:
        """Query companies from the companies table"""
        query = '''
            SELECT 
                comp.id,
                comp.name,
                comp.industry,
                comp.website,
                comp.phone,
                comp.email,
                comp.status,
                COUNT(DISTINCT o.id) as deal_count,
                SUM(CASE WHEN o.stage = 'won' THEN o.value ELSE 0 END) as total_revenue
            FROM companies comp
            LEFT JOIN opportunities o ON o.company_id = comp.id
            WHERE comp.status = 'active'
        '''
        params = []
        
        # Extract industry filter
        industries = ['technology', 'finance', 'healthcare', 'retail', 'manufacturing', 'education']
        for industry in industries:
            if industry in message.lower():
                query += " AND LOWER(comp.industry) LIKE ?"
                params.append(f'%{industry}%')
                break
        
        query += " GROUP BY comp.id ORDER BY comp.name ASC LIMIT 50"
        
        try:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Company query error: {e}")
            return []
    
    def _query_contacts(self, cursor, message: str) -> List[Dict]:
        """Query contacts based on natural language"""
        query = '''
            SELECT c.id, c.name,
                   c.email, c.phone, c.job_title, c.lead_score,
                   c.company as company_name, c.status
            FROM customers c
            WHERE 1=1
        '''
        params = []
        
        # Check for role/title filters
        if 'ceo' in message.lower() or 'executive' in message.lower():
            query += " AND (LOWER(c.job_title) LIKE '%ceo%' OR LOWER(c.job_title) LIKE '%president%' OR LOWER(c.job_title) LIKE '%executive%')"
        elif 'manager' in message.lower():
            query += " AND LOWER(c.job_title) LIKE '%manager%'"
        
        # Check for recent filter
        if 'recent' in message.lower():
            query += " ORDER BY c.created_at DESC LIMIT 50"
        else:
            query += " ORDER BY c.lead_score DESC LIMIT 50"
        
        try:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Contacts query error: {e}")
            return []
    
    def _query_tasks(self, cursor, message: str) -> List[Dict]:
        """Query tasks based on natural language"""
        message_lower = message.lower()
        
        query = '''
            SELECT t.id, t.title, t.description, t.status, 
                   t.priority, t.due_date, t.assigned_to,
                   c.name as customer_name
            FROM tasks t
            LEFT JOIN customers c ON t.customer_id = c.id
            WHERE 1=1
        '''
        params = []
        
        # Filter by status
        if 'pending' in message_lower or 'open' in message_lower or 'active' in message_lower:
            query += " AND t.status = 'pending'"
        elif 'completed' in message_lower or 'done' in message_lower:
            query += " AND t.status = 'completed'"
        elif 'overdue' in message_lower:
            query += " AND t.status = 'pending' AND t.due_date < date('now')"
        
        # Filter by priority
        if 'high priority' in message_lower or 'urgent' in message_lower:
            query += " AND t.priority = 'high'"
        elif 'low priority' in message_lower:
            query += " AND t.priority = 'low'"
        
        query += " ORDER BY t.due_date ASC, t.priority DESC LIMIT 50"
        
        try:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Tasks query error: {e}")
            return []
    
    def _query_recent_interactions(self, cursor, message: str) -> List[Dict]:
        """Query recent interactions"""
        limit = 10
        if 'last 5' in message.lower() or 'recent 5' in message.lower():
            limit = 5
        elif 'last 20' in message.lower():
            limit = 20
        
        query = '''
            SELECT i.id, i.type, i.channel, i.notes,
                   i.created_at, c.name as customer_name,
                   c.company as company_name
            FROM interactions i
            LEFT JOIN customers c ON i.customer_id = c.id
            ORDER BY i.created_at DESC
            LIMIT ?
        '''
        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]
    
    def _query_stalled_deals(self, cursor) -> List[Dict]:
        """Query deals that haven't been updated recently"""
        query = '''
            SELECT o.id, o.title, o.value, o.stage,
                   julianday('now') - julianday(o.updated_at) as days_stalled,
                   c.company as company_name
            FROM opportunities o
            LEFT JOIN customers c ON o.customer_id = c.id
            WHERE o.status = 'open' 
            AND o.stage NOT IN ('won', 'lost')
            AND julianday('now') - julianday(o.updated_at) > 14
            ORDER BY days_stalled DESC
            LIMIT 20
        '''
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def _query_top_customers(self, cursor) -> List[Dict]:
        """Query top customers by deal value"""
        query = '''
            SELECT c.id, c.name, c.company, c.lead_score,
                   COUNT(DISTINCT o.id) as deal_count,
                   SUM(CASE WHEN o.stage = 'won' THEN o.value ELSE 0 END) as total_revenue,
                   MAX(i.created_at) as last_interaction
            FROM customers c
            LEFT JOIN opportunities o ON c.id = o.customer_id
            LEFT JOIN interactions i ON c.id = i.customer_id
            GROUP BY c.id
            HAVING total_revenue > 0
            ORDER BY total_revenue DESC
            LIMIT 10
        '''
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
    
    def _ai_assisted_query(self, cursor, message: str) -> List[Dict]:
        """Use AI to construct complex queries"""
        # For now, return a generic query - can be enhanced later
        cursor.execute("SELECT * FROM customers LIMIT 10")
        return [dict(row) for row in cursor.fetchall()]
    
    def _handle_navigation(self, message: str) -> Dict:
        """Handle navigation requests with fuzzy matching"""
        message_lower = message.lower()
        response = {
            'intent': 'navigate',
            'data': None,
            'navigation_target': None,
            'message': '',
            'actions': ['navigate'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Expanded keyword mapping for better understanding
        section_keywords = {
            'pipeline': ['pipeline', 'deals', 'opportunities', 'sales funnel', 'funnel'],
            'contacts': ['contacts', 'people', 'persons', 'individuals'],
            'companies': ['companies', 'organizations', 'businesses', 'orgs', 'firms'],
            'dashboard': ['dashboard', 'home', 'overview', 'main page'],
            'reports': ['reports', 'analytics', 'reporting', 'insights'],
            'tasks': ['tasks', 'todos', 'to-dos', 'task list'],
            'interactions': ['interactions', 'activities', 'history', 'touchpoints'],
            'settings': ['settings', 'preferences', 'config', 'configuration']
        }
        
        # Find matching section using keywords
        for section, keywords in section_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                response['navigation_target'] = self.navigation_map.get(section, f'/{section}')
                response['message'] = f"Opening {section.title()}..."
                return response
        
        # Use AI for complex/ambiguous requests
        prompt = f"""User navigation request: "{message}"

CRM sections available: dashboard, pipeline, contacts, companies, reports, tasks, interactions, settings

Which section matches their intent? Reply with ONLY the section name (one word) or "unknown"."""

        try:
            ai_section = self.ai_model.generate(prompt, max_length=30).strip().lower()
            for section in self.navigation_map.keys():
                if section in ai_section:
                    response['navigation_target'] = self.navigation_map[section]
                    response['message'] = f"Opening {section.title()}..."
                    return response
        except:
            pass
        
        response['message'] = f"I can help you navigate to: Dashboard, Pipeline, Contacts, Companies, Reports, Tasks, Interactions, or Settings. Where would you like to go?"
        return response
    
    def _handle_create_action(self, message: str, intent_result: Dict) -> Dict:
        """Handle create record actions with AI-powered intelligence and automation"""
        message_lower = message.lower()
        response = {
            'intent': 'create_record',
            'data': None,
            'navigation_target': None,
            'message': '',
            'actions': ['create'],
            'timestamp': datetime.now().isoformat(),
            'needs_input': None  # For multi-step conversations
        }
        
        # Use AI to intelligently extract entity type and data
        extracted = self._ai_extract_entity_and_data(message)
        entity_type = extracted.get('entity_type')
        data = extracted.get('data', {})
        
        # Handle COMPANY creation with multi-step conversation
        if entity_type == 'company' or ('company' in message_lower and entity_type != 'contact'):
            # Check if we have all required data, if not collect step by step
            if not data.get('name'):
                response['message'] = "What's the company name?"
                response['needs_input'] = 'company_name'
            elif not data.get('industry'):
                response['message'] = f"Great! What industry is {data.get('name')} in?\n(e.g., Technology, Healthcare, Finance, Manufacturing, etc.)"
                response['needs_input'] = 'company_industry'
                response['data'] = {'name': data.get('name')}
            elif not data.get('website'):
                response['message'] = f"What's the website for {data.get('name')}?\n(Enter website URL or type 'skip' to skip)"
                response['needs_input'] = 'company_website'
                response['data'] = {'name': data.get('name'), 'industry': data.get('industry')}
            elif not data.get('email'):
                response['message'] = f"What's the contact email for {data.get('name')}?\n(Enter email or type 'skip' to skip)"
                response['needs_input'] = 'company_email'
                response['data'] = {'name': data.get('name'), 'industry': data.get('industry'), 'website': data.get('website')}
            elif not data.get('phone'):
                response['message'] = f"What's the phone number for {data.get('name')}?\n(Enter phone or type 'skip' to skip)"
                response['needs_input'] = 'company_phone'
                response['data'] = {'name': data.get('name'), 'industry': data.get('industry'), 'website': data.get('website'), 'email': data.get('email')}
            else:
                # All data collected, now insert
                try:
                    db = get_db()
                    cursor = db.cursor()
                    
                    # Check if company already exists
                    cursor.execute('SELECT id FROM customers WHERE company = ?', (data.get('name'),))
                    existing = cursor.fetchone()
                    
                    if existing:
                        response['message'] = f"Company '{data.get('name')}' already exists (ID: {existing[0]})"
                        response['data'] = {'company_id': existing[0]}
                    else:
                        # Handle 'skip' values
                        website = data.get('website') if data.get('website') and data.get('website').lower() != 'skip' else ''
                        email = data.get('email') if data.get('email') and data.get('email').lower() != 'skip' else ''
                        phone = data.get('phone') if data.get('phone') and data.get('phone').lower() != 'skip' else ''
                        
                        cursor.execute('''
                            INSERT INTO customers (name, company, industry, website, email, phone, status, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                        ''', (data.get('name'), data.get('name'), data.get('industry'), website, email, phone, 'lead'))
                        db.commit()
                        company_id = cursor.lastrowid
                        
                        # Build detailed success message
                        msg = f"✅ Created company: {data.get('name')}\n"
                        msg += f"📊 Industry: {data.get('industry')}"
                        if website:
                            msg += f"\n🌐 Website: {website}"
                        if email:
                            msg += f"\n📧 Email: {email}"
                        if phone:
                            msg += f"\n📞 Phone: {phone}"
                        
                        response['message'] = msg
                        response['data'] = {'company_id': company_id, 'company_name': data.get('name')}
                except Exception as e:
                    response['message'] = f"❌ Error creating company: {str(e)}"
        
        # Handle CONTACT creation with multi-step conversation
        elif entity_type == 'contact' or 'contact' in message_lower or 'person' in message_lower:
            # Check if we have all required data, if not collect step by step
            if not data.get('first_name'):
                response['message'] = "What's the contact's first name?"
                response['needs_input'] = 'contact_first_name'
            elif not data.get('last_name'):
                response['message'] = f"What's {data.get('first_name')}'s last name?"
                response['needs_input'] = 'contact_last_name'
                response['data'] = {'first_name': data.get('first_name')}
            elif not data.get('email'):
                response['message'] = f"What's the email for {data.get('first_name')} {data.get('last_name')}?\n(Enter email or type 'skip' to skip)"
                response['needs_input'] = 'contact_email'
                response['data'] = {'first_name': data.get('first_name'), 'last_name': data.get('last_name')}
            elif not data.get('phone'):
                response['message'] = f"What's the phone number?\n(Enter phone or type 'skip' to skip)"
                response['needs_input'] = 'contact_phone'
                response['data'] = {'first_name': data.get('first_name'), 'last_name': data.get('last_name'), 'email': data.get('email')}
            elif not data.get('job_title'):
                response['message'] = f"What's their job title?\n(e.g., CEO, Sales Manager, Developer, etc. or type 'skip')"
                response['needs_input'] = 'contact_job_title'
                response['data'] = {'first_name': data.get('first_name'), 'last_name': data.get('last_name'), 'email': data.get('email'), 'phone': data.get('phone')}
            elif not data.get('company'):
                response['message'] = f"Which company does {data.get('first_name')} work for?\n(Enter company name or type 'skip' to skip)"
                response['needs_input'] = 'contact_company'
                response['data'] = {'first_name': data.get('first_name'), 'last_name': data.get('last_name'), 'email': data.get('email'), 'phone': data.get('phone'), 'job_title': data.get('job_title')}
            else:
                # All data collected, now insert into contacts table
                try:
                    db = get_db()
                    cursor = db.cursor()
                    
                    # Try to link to existing company in customers table
                    company_id = None
                    company_name = data.get('company')
                    if company_name and company_name.lower() != 'skip':
                        cursor.execute('SELECT id FROM customers WHERE company = ?', (company_name,))
                        company_row = cursor.fetchone()
                        if company_row:
                            company_id = company_row[0]
                    
                    # Handle 'skip' values
                    email = data.get('email') if data.get('email') and data.get('email').lower() != 'skip' else ''
                    phone = data.get('phone') if data.get('phone') and data.get('phone').lower() != 'skip' else ''
                    job_title = data.get('job_title') if data.get('job_title') and data.get('job_title').lower() != 'skip' else ''
                    
                    # Insert into contacts table
                    cursor.execute('''
                        INSERT INTO contacts (first_name, last_name, email, phone, job_title, company_id, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
                    ''', (data.get('first_name'), data.get('last_name'), email, phone, job_title, company_id, 'lead'))
                    db.commit()
                    contact_id = cursor.lastrowid
                    
                    # Build detailed success message
                    msg = f"✅ Created contact: {data.get('first_name')} {data.get('last_name')}"
                    if job_title:
                        msg += f"\n👔 Title: {job_title}"
                    if company_name and company_name.lower() != 'skip':
                        msg += f"\n🏢 Company: {company_name}"
                        if company_id:
                            msg += f" (linked to existing company)"
                    if email:
                        msg += f"\n📧 Email: {email}"
                    if phone:
                        msg += f"\n📞 Phone: {phone}"
                    
                    response['message'] = msg
                    response['data'] = {'contact_id': contact_id, 'company_id': company_id}
                except Exception as e:
                    response['message'] = f"❌ Error creating contact: {str(e)}"
        
        # Handle DEAL/OPPORTUNITY creation
        elif entity_type == 'deal' or 'deal' in message_lower or 'opportunity' in message_lower:
            if data.get('title'):
                try:
                    db = get_db()
                    cursor = db.cursor()
                    
                    # Try to link to customer if mentioned, otherwise use empty string
                    customer_id = ''
                    if data.get('customer_name'):
                        cursor.execute('SELECT id FROM customers WHERE name LIKE ?', (f'%{data.get("customer_name")}%',))
                        customer_row = cursor.fetchone()
                        if customer_row:
                            customer_id = customer_row[0]
                    
                    cursor.execute('''
                        INSERT INTO opportunities (title, value, stage, status, expected_close_date, created_at, updated_at, customer_id)
                        VALUES (?, ?, ?, ?, ?, datetime('now'), datetime('now'), ?)
                    ''', (data.get('title'), data.get('value', 0), data.get('stage', 'lead'), 'open', 
                          data.get('close_date', ''), customer_id))
                    db.commit()
                    deal_id = cursor.lastrowid
                    
                    msg = f"✅ Created deal: {data.get('title')}"
                    if data.get('value'):
                        msg += f" (${data.get('value'):,.0f})"
                    if data.get('stage'):
                        msg += f"\n📊 Stage: {data.get('stage')}"
                    
                    response['message'] = msg
                    response['data'] = {'deal_id': deal_id}
                except Exception as e:
                    response['message'] = f"❌ Error creating deal: {str(e)}"
            else:
                response['message'] = "What's the deal title? (e.g., 'Enterprise License' or 'Q1 Partnership')"
                response['needs_input'] = 'deal_title'
        
        # Handle TASK creation with multi-step conversation
        elif entity_type == 'task' or 'task' in message_lower:
            # Check if we have all required data, if not collect step by step
            if not data.get('title'):
                response['message'] = "What task would you like to create?"
                response['needs_input'] = 'task_title'
            elif not data.get('description'):
                response['message'] = f"Please provide a description for the task '{data.get('title')}':\n(Type 'skip' to skip)"
                response['needs_input'] = 'task_description'
                response['data'] = {'title': data.get('title')}
            elif not data.get('priority'):
                response['message'] = f"What's the priority for this task?\n(Options: high, medium, low. Default: medium)"
                response['needs_input'] = 'task_priority'
                response['data'] = {'title': data.get('title'), 'description': data.get('description')}
            elif not data.get('due_date'):
                response['message'] = f"When is this task due?\n(e.g., '2024-12-31', 'next week', or type 'skip' to skip)"
                response['needs_input'] = 'task_due_date'
                response['data'] = {'title': data.get('title'), 'description': data.get('description'), 'priority': data.get('priority')}
            else:
                # All data collected, now insert
                try:
                    db = get_db()
                    cursor = db.cursor()
                    
                    # Handle 'skip' values
                    description = data.get('description') if data.get('description') and data.get('description').lower() != 'skip' else ''
                    priority = data.get('priority') if data.get('priority') and data.get('priority').lower() not in ['skip', ''] else 'medium'
                    # Validate priority
                    if priority.lower() not in ['high', 'medium', 'low']:
                        priority = 'medium'
                    else:
                        priority = priority.lower()
                    due_date = data.get('due_date') if data.get('due_date') and data.get('due_date').lower() != 'skip' else ''
                    
                    cursor.execute('''
                        INSERT INTO tasks (title, description, status, priority, due_date, created_at)
                        VALUES (?, ?, ?, ?, ?, datetime('now'))
                    ''', (data.get('title'), description, 'pending', priority, due_date))
                    db.commit()
                    task_id = cursor.lastrowid
                    
                    # Build detailed success message
                    msg = f"✅ Created task: {data.get('title')}"
                    if description:
                        msg += f"\n📝 Description: {description}"
                    msg += f"\n🎯 Priority: {priority}"
                    if due_date:
                        msg += f"\n⏰ Due: {due_date}"
                    
                    response['message'] = msg
                    response['data'] = {'task_id': task_id}
                except Exception as e:
                    response['message'] = f"❌ Error creating task: {str(e)}"
        
        # Handle INTERACTION logging
        elif 'log' in message_lower or 'interaction' in message_lower or any(word in message_lower for word in ['call', 'meeting', 'email', 'note']):
            interaction_type = 'note'
            if 'call' in message_lower:
                interaction_type = 'call'
            elif 'meeting' in message_lower:
                interaction_type = 'meeting'
            elif 'email' in message_lower:
                interaction_type = 'email'
            
            try:
                db = get_db()
                cursor = db.cursor()
                
                # Try to find customer mentioned, otherwise use empty string
                customer_id = ''
                if data.get('customer_name'):
                    cursor.execute('SELECT id FROM customers WHERE name LIKE ?', (f'%{data.get("customer_name")}%',))
                    customer_row = cursor.fetchone()
                    if customer_row:
                        customer_id = customer_row[0]
                
                cursor.execute('''
                    INSERT INTO interactions (customer_id, type, notes, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                ''', (customer_id, interaction_type, data.get('notes', message)))
                db.commit()
                
                response['message'] = f"✅ Logged {interaction_type}"
                if customer_id:
                    response['message'] += f" for customer (ID: {customer_id})"
                response['data'] = {'interaction_id': cursor.lastrowid}
            except Exception as e:
                response['message'] = f"❌ Error logging interaction: {str(e)}"
        
        # Unknown entity type - ask user
        else:
            response['message'] = "What would you like to create?\n• Company\n• Contact\n• Deal/Opportunity\n• Task\n• Log interaction"
            response['needs_input'] = 'entity_type'
        
        return response
    
    def _handle_delete_action(self, message: str, intent_result: Dict) -> Dict:
        """Handle delete record actions"""
        message_lower = message.lower()
        response = {
            'intent': 'delete_record',
            'data': None,
            'navigation_target': None,
            'message': '',
            'actions': ['delete'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Extract what to delete
        if 'contact' in message_lower or 'customer' in message_lower:
            name = self._extract_name(message)
            if name:
                try:
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT id, name FROM customers WHERE LOWER(name) LIKE ?", (f'%{name.lower()}%',))
                    result = cursor.fetchone()
                    if result:
                        cursor.execute("DELETE FROM customers WHERE id = ?", (result[0],))
                        db.commit()
                        response['message'] = f"✅ Deleted contact: {result[1]}"
                    else:
                        response['message'] = f"❌ Contact '{name}' not found"
                except Exception as e:
                    response['message'] = f"Error deleting contact: {str(e)}"
            else:
                response['message'] = "Please specify which contact to delete. Example: 'Delete contact John Doe'"
        
        elif 'company' in message_lower:
            name = self._extract_name(message)
            if name:
                response['message'] = f"To delete company '{name}', please confirm in the Companies page"
            else:
                response['message'] = "Please specify which company to delete"
        
        elif 'deal' in message_lower:
            title = self._extract_deal_title(message)
            if title:
                try:
                    db = get_db()
                    cursor = db.cursor()
                    cursor.execute("SELECT id, title FROM opportunities WHERE LOWER(title) LIKE ?", (f'%{title.lower()}%',))
                    result = cursor.fetchone()
                    if result:
                        cursor.execute("DELETE FROM opportunities WHERE id = ?", (result[0],))
                        db.commit()
                        response['message'] = f"✅ Deleted deal: {result[1]}"
                    else:
                        response['message'] = f"❌ Deal '{title}' not found"
                except Exception as e:
                    response['message'] = f"Error deleting deal: {str(e)}"
            else:
                response['message'] = "Please specify which deal to delete"
        
        else:
            response['message'] = "What would you like to delete? (contact, company, or deal)"
        
        return response
    
    def _handle_update_action(self, message: str, intent_result: Dict) -> Dict:
        """Handle update record actions - especially pipeline stage changes"""
        message_lower = message.lower()
        response = {
            'intent': 'update_record',
            'data': None,
            'navigation_target': None,
            'message': '',
            'actions': ['update'],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Handle pipeline stage changes
            if any(word in message_lower for word in ['move', 'change', 'update', 'set']) and any(word in message_lower for word in ['deal', 'opportunity', 'stage', 'status', 'pipeline']):
                # Extract deal identifier (ID or name)
                deal_id = None
                deal_match = re.search(r'deal\s+(?:id\s+)?(\d+)', message_lower)
                if deal_match:
                    deal_id = int(deal_match.group(1))
                else:
                    # Try to find deal by name
                    deal_name_match = re.search(r'deal\s+["\']?([A-Za-z0-9\s-]+?)["\']?\s+to', message)
                    if deal_name_match:
                        deal_name = deal_name_match.group(1).strip()
                        cursor.execute('SELECT id FROM opportunities WHERE title LIKE ?', (f'%{deal_name}%',))
                        deal_row = cursor.fetchone()
                        if deal_row:
                            deal_id = deal_row[0]
                
                # Extract new stage
                stage_keywords = {
                    'lead': ['lead', 'new'],
                    'qualification': ['qualification', 'qualify', 'qualified'],
                    'proposal': ['proposal', 'quote', 'quoted'],
                    'negotiation': ['negotiation', 'negotiate', 'negotiating'],
                    'closed_won': ['won', 'closed won', 'close won', 'victory', 'success'],
                    'closed_lost': ['lost', 'closed lost', 'close lost', 'failed']
                }
                
                new_stage = None
                for stage, keywords in stage_keywords.items():
                    if any(keyword in message_lower for keyword in keywords):
                        new_stage = stage
                        break
                
                if deal_id and new_stage:
                    # Update the deal stage
                    cursor.execute('''
                        UPDATE opportunities 
                        SET stage = ?, 
                            status = ?,
                            updated_at = datetime('now')
                        WHERE id = ?
                    ''', (new_stage, 'closed' if 'closed' in new_stage else 'open', deal_id))
                    db.commit()
                    
                    # Get deal title for confirmation
                    cursor.execute('SELECT title FROM opportunities WHERE id = ?', (deal_id,))
                    deal = cursor.fetchone()
                    deal_title = deal[0] if deal else f"Deal #{deal_id}"
                    
                    response['message'] = f"✅ Moved '{deal_title}' to {new_stage.replace('_', ' ').title()}"
                    response['data'] = {'deal_id': deal_id, 'new_stage': new_stage}
                elif deal_id and not new_stage:
                    response['message'] = "What stage should I move it to?\n• Lead\n• Qualification\n• Proposal\n• Negotiation\n• Closed Won\n• Closed Lost"
                elif new_stage and not deal_id:
                    response['message'] = "Which deal should I update? Please provide the deal ID or name."
                else:
                    response['message'] = "Please specify which deal and what stage. Example: 'Move deal 5 to negotiation'"
            
            # Handle task status updates
            elif 'task' in message_lower and any(word in message_lower for word in ['complete', 'done', 'finish', 'mark']):
                task_id = None
                task_match = re.search(r'task\s+(?:id\s+)?(\d+)', message_lower)
                if task_match:
                    task_id = int(task_match.group(1))
                
                if task_id:
                    cursor.execute('''
                        UPDATE tasks 
                        SET status = 'completed', 
                            updated_at = datetime('now')
                        WHERE id = ?
                    ''', (task_id,))
                    db.commit()
                    
                    cursor.execute('SELECT title FROM tasks WHERE id = ?', (task_id,))
                    task = cursor.fetchone()
                    task_title = task[0] if task else f"Task #{task_id}"
                    
                    response['message'] = f"✅ Marked task '{task_title}' as completed"
                    response['data'] = {'task_id': task_id, 'status': 'completed'}
                else:
                    response['message'] = "Which task should I mark as complete? Please provide the task ID."
            
            else:
                response['message'] = "What would you like to update?\n• Move deal to different stage\n• Mark task as complete\n• Update contact information"
        
        except Exception as e:
            response['message'] = f"❌ Error updating record: {str(e)}"
        
        return response
    
    def _handle_analytics_query(self, message: str) -> Dict:
        """Handle analytics and reporting queries"""
        message_lower = message.lower()
        response = {
            'intent': 'analytics',
            'data': {},
            'navigation_target': '/reports',
            'message': '',
            'actions': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            db = get_db()
            cursor = db.cursor()
            
            # How many deals closed this quarter/month/week?
            if 'how many' in message_lower and 'deal' in message_lower:
                time_period = self._extract_time_period(message)
                
                query = "SELECT COUNT(*) as count, SUM(value) as total FROM opportunities WHERE stage = 'won'"
                if time_period:
                    query += f" AND close_date >= date('now', '-{time_period} days')"
                
                cursor.execute(query)
                result = cursor.fetchone()
                count = result[0] or 0
                total = result[1] or 0
                
                response['data'] = {'count': count, 'total_value': total}
                response['message'] = f"You closed {count} deals worth ${total:,.2f} in the specified period."
            
            # Total revenue
            elif 'revenue' in message_lower or 'sales' in message_lower:
                time_period = self._extract_time_period(message)
                
                query = "SELECT SUM(value) as total FROM opportunities WHERE stage = 'won'"
                if time_period:
                    query += f" AND close_date >= date('now', '-{time_period} days')"
                
                cursor.execute(query)
                total = cursor.fetchone()[0] or 0
                
                response['data'] = {'total_revenue': total}
                response['message'] = f"Total revenue: ${total:,.2f}"
            
            # Pipeline value
            elif 'pipeline' in message_lower:
                cursor.execute("SELECT SUM(value) FROM opportunities WHERE status = 'open' AND stage NOT IN ('won', 'lost')")
                total = cursor.fetchone()[0] or 0
                
                response['data'] = {'pipeline_value': total}
                response['message'] = f"Current pipeline value: ${total:,.2f}"
            
            # Conversion rate
            elif 'conversion' in message_lower:
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN stage = 'won' THEN 1 ELSE 0 END) as won
                    FROM opportunities
                    WHERE stage IN ('won', 'lost')
                ''')
                result = cursor.fetchone()
                total = result[0] or 0
                won = result[1] or 0
                rate = (won / total * 100) if total > 0 else 0
                
                response['data'] = {'conversion_rate': rate}
                response['message'] = f"Conversion rate: {rate:.1f}% ({won} won out of {total} closed deals)"
            
            else:
                # Use AI to generate analytics response
                response['message'] = self._generate_analytics_with_ai(cursor, message)
            
        except Exception as e:
            print(f"Analytics query error: {e}")
            response['message'] = "I encountered an error processing your analytics query."
        
        return response
    
    def _generate_analytics_with_ai(self, cursor, message: str) -> str:
        """Generate analytics response using AI"""
        # Gather basic stats
        cursor.execute("SELECT COUNT(*) FROM opportunities WHERE stage = 'won'")
        won_deals = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(value) FROM opportunities WHERE stage = 'won'")
        revenue = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM customers WHERE status IN ('lead', 'qualified')")
        leads = cursor.fetchone()[0]
        
        prompt = f"""User asked: "{message}"

Current CRM stats:
- Won deals: {won_deals}
- Total revenue: ${revenue:,.2f}
- Active leads: {leads}

Provide a brief, helpful analytics answer (2-3 sentences max)."""

        try:
            return self.ai_model.generate(prompt, max_length=150)
        except:
            return f"Current stats: {won_deals} won deals, ${revenue:,.2f} revenue, {leads} active leads."
    
    def _generate_ai_response(self, message: str) -> str:
        """Generate AI response for general queries"""
        prompt = f"""You are a helpful CRM assistant. User said: "{message}"

Respond naturally and helpfully. Keep it under 100 words."""

        try:
            response = self.ai_model.generate(prompt, max_length=200)
            # Clean up any thinking tags
            response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            return response if response else "I'm here to help! What would you like to know?"
        except:
            return "I'm here to help! You can ask me about your deals, contacts, companies, or navigate to different sections."
    
    # Helper methods
    def _extract_time_period(self, message: str) -> Optional[int]:
        """Extract time period from message (returns days)"""
        message_lower = message.lower()
        
        if 'today' in message_lower:
            return 1
        elif 'yesterday' in message_lower:
            return 1
        elif 'this week' in message_lower or 'last week' in message_lower:
            return 7
        elif 'this month' in message_lower or 'last month' in message_lower:
            return 30
        elif 'this quarter' in message_lower or 'last quarter' in message_lower:
            return 90
        elif 'this year' in message_lower or 'last year' in message_lower:
            return 365
        
        # Extract specific numbers
        match = re.search(r'(\d+)\s*(day|week|month)', message_lower)
        if match:
            num = int(match.group(1))
            unit = match.group(2)
            if unit == 'day':
                return num
            elif unit == 'week':
                return num * 7
            elif unit == 'month':
                return num * 30
        
        return None
    
    def _extract_source(self, message: str) -> Optional[str]:
        """Extract lead source from message"""
        sources = ['linkedin', 'facebook', 'google', 'referral', 'website', 'email', 'cold call']
        message_lower = message.lower()
        
        for source in sources:
            if source in message_lower:
                return source
        
        return None
    
    # ===== ACTION HANDLING METHODS =====
    # Note: _handle_create_action is defined earlier in the file (line ~722)
    
    def _handle_analytics_query(self, message: str) -> Dict:
        """Handle complex analytics queries"""
        message_lower = message.lower()
        
        try:
            db = get_db()
            cursor = db.cursor()
            
            response = {
                'intent': 'analytics',
                'data': {},
                'message': '',
                'charts': [],
                'timestamp': datetime.now().isoformat()
            }
            
            # "How many deals closed last quarter?"
            if 'how many' in message_lower and any(word in message_lower for word in ['deal', 'close', 'won']):
                period = self._extract_time_period(message)
                if period:
                    date_filter = f"datetime(actual_close_date) >= datetime('now', '-{period} days')"
                else:
                    # Last quarter
                    date_filter = "datetime(actual_close_date) >= datetime('now', 'start of month', '-3 months')"
                
                cursor.execute(f"""
                    SELECT COUNT(*), SUM(value)
                    FROM opportunities
                    WHERE status = 'won' AND {date_filter}
                """)
                
                row = cursor.fetchone()
                count = row[0] if row else 0
                total_value = row[1] if row and row[1] else 0
                
                response['data'] = {
                    'deals_closed': count,
                    'total_value': total_value
                }
                response['message'] = f"📊 **{count} deals closed** with a total value of **${total_value:,.2f}**"
                return response
            
            # "Revenue trends"
            elif 'revenue' in message_lower and ('trend' in message_lower or 'growth' in message_lower):
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m', actual_close_date) as month,
                        COUNT(*) as deals,
                        SUM(value) as revenue
                    FROM opportunities
                    WHERE status = 'won' 
                    AND actual_close_date >= date('now', '-6 months')
                    GROUP BY month
                    ORDER BY month
                """)
                
                rows = cursor.fetchall()
                monthly_data = [{'month': r[0], 'deals': r[1], 'revenue': r[2]} for r in rows]
                
                if len(monthly_data) >= 2:
                    recent_revenue = monthly_data[-1]['revenue'] or 0
                    previous_revenue = monthly_data[-2]['revenue'] or 1
                    growth = ((recent_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
                    
                    response['data'] = {
                        'monthly_data': monthly_data,
                        'growth_rate': growth
                    }
                    response['message'] = f"📈 **Revenue {'grew' if growth > 0 else 'declined'} by {abs(growth):.1f}%** this month"
                    response['charts'] = [{
                        'type': 'line',
                        'data': monthly_data
                    }]
                else:
                    response['message'] = "Not enough data for trend analysis (need at least 2 months)"
                
                return response
            
            # "Conversion rate"
            elif 'conversion' in message_lower:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as won
                    FROM opportunities
                    WHERE created_at >= datetime('now', '-30 days')
                """)
                
                row = cursor.fetchone()
                total = row[0] if row else 0
                won = row[1] if row else 0
                conversion_rate = (won / total * 100) if total > 0 else 0
                
                response['data'] = {
                    'total_opportunities': total,
                    'won_opportunities': won,
                    'conversion_rate': conversion_rate
                }
                response['message'] = f"📊 **{conversion_rate:.1f}% conversion rate** ({won}/{total} deals won in last 30 days)"
                return response
            
            # "Pipeline value"
            elif 'pipeline' in message_lower and ('value' in message_lower or 'worth' in message_lower):
                cursor.execute("""
                    SELECT 
                        stage,
                        COUNT(*) as count,
                        SUM(value) as total_value
                    FROM opportunities
                    WHERE status = 'open'
                    GROUP BY stage
                """)
                
                rows = cursor.fetchall()
                pipeline_data = [{'stage': r[0], 'count': r[1], 'value': r[2]} for r in rows]
                total_pipeline = sum(p['value'] or 0 for p in pipeline_data)
                
                response['data'] = {
                    'by_stage': pipeline_data,
                    'total_value': total_pipeline
                }
                response['message'] = f"💰 **Total pipeline value: ${total_pipeline:,.2f}**\n\n"
                for p in pipeline_data:
                    response['message'] += f"- {p['stage'].title()}: {p['count']} deals (${p['value'] or 0:,.0f})\n"
                
                return response
            
            # "Top performing [salesperson/product/industry]"
            elif 'top' in message_lower and 'perform' in message_lower:
                cursor.execute("""
                    SELECT 
                        c.name as salesperson,
                        COUNT(o.id) as deals_won,
                        SUM(o.value) as total_revenue
                    FROM opportunities o
                    JOIN customers c ON o.customer_id = c.id
                    WHERE o.status = 'won'
                    AND o.actual_close_date >= date('now', '-90 days')
                    GROUP BY salesperson
                    ORDER BY total_revenue DESC
                    LIMIT 5
                """)
                
                rows = cursor.fetchall()
                top_performers = [{'name': r[0], 'deals': r[1], 'revenue': r[2]} for r in rows]
                
                response['data'] = {'top_performers': top_performers}
                response['message'] = "🏆 **Top Performers (Last 90 Days)**:\n\n"
                for i, p in enumerate(top_performers, 1):
                    response['message'] += f"{i}. {p['name']} - {p['deals']} deals (${p['revenue'] or 0:,.0f})\n"
                
                return response
            
            # General analytics
            else:
                return self._handle_general_analytics(message, cursor)
                
        except Exception as e:
            print(f"Error in analytics query: {e}")
            print(traceback.format_exc())
            return {
                'intent': 'analytics',
                'success': False,
                'message': f'Error processing analytics: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_crm_summary(self, cursor, message: str) -> Dict:
        """Handle comprehensive CRM summary requests"""
        try:
            response = {
                'intent': 'query_data',
                'data': {},
                'navigation_target': None,
                'message': '',
                'timestamp': datetime.now().isoformat()
            }
            
            # Get counts for all major entities
            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM customers WHERE status = 'lead'")
            total_leads = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM companies WHERE status = 'active'")
            total_companies = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*), SUM(value) FROM opportunities WHERE status = 'open'")
            row = cursor.fetchone()
            open_deals = row[0]
            pipeline_value = row[1] or 0
            
            cursor.execute("SELECT COUNT(*), SUM(value) FROM opportunities WHERE stage = 'won'")
            row = cursor.fetchone()
            won_deals = row[0]
            total_revenue = row[1] or 0
            
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
            pending_tasks = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM interactions WHERE DATE(created_at) >= DATE('now', '-7 days')")
            recent_interactions = cursor.fetchone()[0]
            
            # Get top leads
            cursor.execute("""
                SELECT name, company, lead_score 
                FROM customers 
                WHERE status = 'lead' 
                ORDER BY lead_score DESC 
                LIMIT 3
            """)
            top_leads = [{'name': r[0], 'company': r[1], 'score': r[2]} for r in cursor.fetchall()]
            
            # Get upcoming tasks
            cursor.execute("""
                SELECT title, due_date, priority 
                FROM tasks 
                WHERE status = 'pending' 
                ORDER BY due_date ASC 
                LIMIT 3
            """)
            upcoming_tasks = [{'title': r[0], 'due_date': r[1], 'priority': r[2]} for r in cursor.fetchall()]
            
            # Build comprehensive summary
            response['data'] = {
                'customers': total_customers,
                'leads': total_leads,
                'companies': total_companies,
                'open_deals': open_deals,
                'pipeline_value': pipeline_value,
                'won_deals': won_deals,
                'total_revenue': total_revenue,
                'pending_tasks': pending_tasks,
                'recent_interactions': recent_interactions,
                'top_leads': top_leads,
                'upcoming_tasks': upcoming_tasks
            }
            
            response['message'] = f"""📊 **CRM Summary Overview**

**Customers & Leads**
• Total Customers: {total_customers}
• Active Leads: {total_leads}
• Companies: {total_companies}

**Sales Pipeline**
• Open Deals: {open_deals} (${pipeline_value:,.2f})
• Won Deals: {won_deals} (${total_revenue:,.2f} revenue)

**Activity**
• Pending Tasks: {pending_tasks}
• Recent Interactions (7 days): {recent_interactions}

**Top 3 Leads:**
"""
            
            for i, lead in enumerate(top_leads, 1):
                response['message'] += f"{i}. {lead['name']} - {lead['company']} (Score: {lead['score']})\n"
            
            if upcoming_tasks:
                response['message'] += f"\n**Upcoming Tasks:**\n"
                for i, task in enumerate(upcoming_tasks, 1):
                    response['message'] += f"{i}. {task['title']} - Due: {task['due_date']} ({task['priority']} priority)\n"
            
            return response
            
        except Exception as e:
            print(f"CRM summary error: {e}")
            print(traceback.format_exc())
            return {
                'intent': 'query_data',
                'message': f'Error generating CRM summary: {str(e)}',
                'data': {},
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_required_fields(self, action_type: str) -> List[str]:
        """Get required fields for each action type"""
        fields_map = {
            'add_contact': ['name', 'email', 'company'],
            'add_company': ['name', 'industry'],
            'log_interaction': ['customer_id', 'type', 'notes'],
            'create_deal': ['customer_id', 'title', 'value'],
            'create_task': ['title', 'due_date']
        }
        return fields_map.get(action_type, [])
    
    def _handle_email_drafting(self, message: str) -> Dict:
        """Handle email drafting requests"""
        if not self.email_automation:
            return {
                'intent': 'draft_email',
                'success': False,
                'message': 'Email automation not available',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Extract intent and recipient from message
            message_lower = message.lower()
            
            # Determine email intent
            email_intent = 'follow_up'
            if 'introduction' in message_lower or 'introduce' in message_lower:
                email_intent = 'introduction'
            elif 'proposal' in message_lower:
                email_intent = 'proposal'
            elif 'follow' in message_lower:
                email_intent = 'follow_up'
            elif 'thank' in message_lower:
                email_intent = 'thank_you'
            
            # Determine tone
            tone = 'professional'
            if 'friendly' in message_lower:
                tone = 'friendly'
            elif 'urgent' in message_lower:
                tone = 'urgent'
            elif 'formal' in message_lower:
                tone = 'professional'
            
            # Mock recipient data (in production, would extract from message or query DB)
            recipient_data = {
                'name': 'Valued Customer',
                'company': 'Their Company',
                'job_title': 'Decision Maker'
            }
            
            # Draft the email
            result = self.email_automation.draft_email(
                intent=email_intent,
                recipient_data=recipient_data,
                tone=tone,
                context=message
            )
            
            if result.get('success'):
                return {
                    'intent': 'draft_email',
                    'success': True,
                    'data': result,
                    'message': f"📧 **Email Draft Ready** ({tone} tone)\n\n**Subject:** {result['subject']}\n\n**Body:**\n{result['body'][:300]}...\n\n✨ Click to view full email and customize",
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'intent': 'draft_email',
                    'success': False,
                    'message': result.get('message', 'Failed to draft email'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error drafting email: {e}")
            print(traceback.format_exc())
            return {
                'intent': 'draft_email',
                'success': False,
                'message': f'Error drafting email: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_data_enrichment(self, message: str) -> Dict:
        """Handle data enrichment requests"""
        if not self.data_enrichment:
            return {
                'intent': 'enrich_data',
                'success': False,
                'message': 'Data enrichment not available',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            message_lower = message.lower()
            
            # Check if enriching company or contact
            if 'company' in message_lower or 'organization' in message_lower:
                # Extract company name or website
                # Simplified: extract from message
                company_data = {'name': 'Example Company'}
                result = self.data_enrichment.enrich_company(company_data)
            elif 'contact' in message_lower or 'person' in message_lower:
                contact_data = {'name': 'Example Contact'}
                result = self.data_enrichment.enrich_contact(contact_data)
            else:
                # Try to extract website URL
                url_pattern = r'https?://[^\s]+'
                urls = re.findall(url_pattern, message)
                if urls:
                    result = self.data_enrichment.auto_enrich_from_website(urls[0])
                else:
                    return {
                        'intent': 'enrich_data',
                        'success': False,
                        'message': 'Please specify what you want to enrich (company, contact, or provide a website URL)',
                        'timestamp': datetime.now().isoformat()
                    }
            
            if result.get('success'):
                enriched_data = result.get('data', {})
                fields_enriched = result.get('fields_enriched', [])
                
                message_text = f"✨ **Data Enriched Successfully!**\n\n"
                message_text += f"**New fields added:** {', '.join(fields_enriched[:5])}\n\n"
                
                # Show sample of enriched data
                for key, value in list(enriched_data.items())[:5]:
                    if value and key not in ['enriched', 'enriched_at']:
                        message_text += f"- **{key.replace('_', ' ').title()}:** {value}\n"
                
                return {
                    'intent': 'enrich_data',
                    'success': True,
                    'data': enriched_data,
                    'message': message_text,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'intent': 'enrich_data',
                    'success': False,
                    'message': result.get('message', 'Failed to enrich data'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error enriching data: {e}")
            print(traceback.format_exc())
            return {
                'intent': 'enrich_data',
                'success': False,
                'message': f'Error enriching data: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_sentiment_analysis(self, message: str) -> Dict:
        """Handle sentiment analysis requests"""
        if not self.email_automation:
            return {
                'intent': 'analyze_sentiment',
                'success': False,
                'message': 'Sentiment analysis not available',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Extract the message to analyze
            # Look for quotes or "analyze this:" pattern
            text_to_analyze = message
            if '"' in message:
                matches = re.findall(r'"([^"]*)"', message)
                if matches:
                    text_to_analyze = matches[0]
            elif 'analyze:' in message.lower():
                text_to_analyze = message.split('analyze:', 1)[1].strip()
            elif 'message:' in message.lower():
                text_to_analyze = message.split('message:', 1)[1].strip()
            
            result = self.email_automation.analyze_sentiment(text_to_analyze)
            
            if result.get('success'):
                sentiment = result.get('sentiment', {})
                urgency = result.get('urgency', 'medium')
                concerns = result.get('concerns', [])
                recommended_tone = result.get('recommended_tone', 'professional')
                
                message_text = f"🎭 **Sentiment Analysis Complete**\n\n"
                message_text += f"**Sentiment:** {sentiment.get('type', 'neutral').title()} ({sentiment.get('score', 50)}/100)\n"
                message_text += f"**Primary Emotion:** {sentiment.get('emotion', 'neutral').title()}\n"
                message_text += f"**Urgency Level:** {urgency.upper()}\n\n"
                
                if concerns:
                    message_text += f"**Key Concerns:**\n"
                    for concern in concerns[:3]:
                        message_text += f"- {concern}\n"
                    message_text += "\n"
                
                message_text += f"**Recommended Response Tone:** {recommended_tone.title()}\n"
                message_text += f"**Requires Immediate Attention:** {'Yes ⚠️' if result.get('requires_immediate_attention') else 'No'}"
                
                return {
                    'intent': 'analyze_sentiment',
                    'success': True,
                    'data': result,
                    'message': message_text,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'intent': 'analyze_sentiment',
                    'success': False,
                    'message': result.get('message', 'Failed to analyze sentiment'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            print(traceback.format_exc())
            return {
                'intent': 'analyze_sentiment',
                'success': False,
                'message': f'Error analyzing sentiment: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_send_email(self, message: str) -> Dict[str, Any]:
        """Handle sending emails from CRM"""
        try:
            import re
            import json
            
            # Extract email address using regex
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, message)
            
            # Extract subject if mentioned
            subject_match = re.search(r'(?:subject|about|regarding)[\s:]+([^\n]+)', message, re.IGNORECASE)
            subject = subject_match.group(1).strip() if subject_match else "CRM Follow-up"
            
            # If email found, create draft
            if emails:
                to_email = emails[0]
                
                # Try to find contact name
                db = get_db()
                cursor = db.cursor()
                cursor.execute("SELECT first_name || ' ' || last_name as name FROM contacts WHERE LOWER(email) = ?", (to_email.lower(),))
                contact = cursor.fetchone()
                if not contact:
                    cursor.execute("SELECT name FROM customers WHERE LOWER(email) = ?", (to_email.lower(),))
                    contact = cursor.fetchone()
                
                contact_name = contact[0] if contact else to_email
                
                return {
                    'intent': 'send_email',
                    'success': True,
                    'action': 'draft_ready',
                    'data': {
                        'to': to_email,
                        'to_name': contact_name,
                        'subject': subject
                    },
                    'message': f"📧 Ready to send email to {contact_name} ({to_email})\n\nSubject: {subject}\n\nWhat would you like to say in the email?",
                    'actions': ['send', 'edit', 'cancel'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # No email found - ask for recipient
            # Check if there are recent contacts to suggest
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT DISTINCT first_name || ' ' || last_name as name, email 
                FROM contacts 
                WHERE email IS NOT NULL AND email != '' 
                ORDER BY updated_at DESC 
                LIMIT 5
            """)
            recent_contacts = cursor.fetchall()
            
            if not recent_contacts:
                cursor.execute("""
                    SELECT DISTINCT name, email 
                    FROM customers 
                    WHERE email IS NOT NULL AND email != '' 
                    ORDER BY updated_at DESC 
                    LIMIT 5
                """)
                recent_contacts = cursor.fetchall()
            
            suggestions = "\n\nRecent contacts:\n" + "\n".join([f"• {c[0]} ({c[1]})" for c in recent_contacts[:3]]) if recent_contacts else ""
            
            return {
                'intent': 'send_email',
                'success': False,
                'needs_input': 'recipient_email',
                'message': f'📧 Who would you like to send an email to? Please provide their email address.{suggestions}',
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"Error handling send email: {e}")
            import traceback
            traceback.print_exc()
            return {
                'intent': 'send_email',
                'success': False,
                'message': f'Error: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    def _handle_email_sync(self, message: str) -> Dict[str, Any]:
        """Handle email syncing"""
        try:
            from modules.email_integration import EmailIntegration
            email_integration = EmailIntegration()
            
            # Get user's email accounts
            cursor = email_integration.db.cursor()
            cursor.execute("""
                SELECT id, email_address, provider 
                FROM email_accounts 
                WHERE is_active = 1 AND sync_enabled = 1
                LIMIT 5
            """)
            
            accounts = cursor.fetchall()
            
            if not accounts:
                return {
                    'intent': 'sync_emails',
                    'success': False,
                    'message': '📧 No email accounts configured for syncing.\n\nPlease add an email account in Settings > Email Integration.',
                    'navigation_target': '/settings',
                    'timestamp': datetime.now().isoformat()
                }
            
            total_synced = 0
            total_logged = 0
            sync_results = []
            
            for account_id, email_address, provider in accounts:
                result = email_integration.sync_emails(account_id, days_back=7, auto_log=True)
                
                if result.get('success'):
                    total_synced += result.get('synced', 0)
                    total_logged += result.get('logged_interactions', 0)
                    sync_results.append({
                        'account': email_address,
                        'synced': result.get('synced', 0),
                        'logged': result.get('logged_interactions', 0)
                    })
            
            message_text = f"✅ **Email Sync Complete**\n\n"
            message_text += f"**Total Emails Synced:** {total_synced}\n"
            message_text += f"**Auto-logged Interactions:** {total_logged}\n\n"
            message_text += "**Accounts Synced:**\n"
            
            for result in sync_results:
                message_text += f"- {result['account']}: {result['synced']} emails, {result['logged']} logged\n"
            
            return {
                'intent': 'sync_emails',
                'success': True,
                'data': {
                    'total_synced': total_synced,
                    'total_logged': total_logged,
                    'accounts': sync_results
                },
                'message': message_text,
                'navigation_target': '/interactions',
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"Error syncing emails: {e}")
            print(traceback.format_exc())
            return {
                'intent': 'sync_emails',
                'success': False,
                'message': f'Error syncing emails: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }
    
    # ==================== DATA EXTRACTION HELPERS ====================
    
    def _ai_extract_entity_and_data(self, message: str) -> Dict:
        """Use AI to intelligently extract entity type and data from message"""
        # For now, use fallback directly for better reliability and speed
        # AI extraction can be re-enabled later with better prompt engineering
        print(f"🔍 Extracting from: {message}")
        return self._fallback_extract_entity_and_data(message)
    
    def _fallback_extract_entity_and_data(self, message: str) -> Dict:
        """Fallback extraction using regex patterns"""
        message_lower = message.lower()
        result = {'entity_type': 'unknown', 'data': {}}
        
        print(f"🔄 Fallback extraction for: {message}")
        
        # Detect entity type
        if 'company' in message_lower or 'organization' in message_lower:
            result['entity_type'] = 'company'
            result['data'] = self._extract_company_data(message)
        elif 'contact' in message_lower or 'person' in message_lower:
            result['entity_type'] = 'contact'
            result['data'] = self._extract_contact_data(message)
        elif 'deal' in message_lower or 'opportunity' in message_lower:
            result['entity_type'] = 'deal'
            result['data'] = self._extract_deal_data(message)
            print(f"📊 Deal data extracted: {result['data']}")
        elif 'task' in message_lower:
            result['entity_type'] = 'task'
            result['data'] = self._extract_task_data(message)
        elif any(word in message_lower for word in ['log', 'call', 'meeting', 'interaction']):
            result['entity_type'] = 'interaction'
            result['data'] = self._extract_interaction_data(message)
        
        print(f"✓ Fallback result: {result['entity_type']} - {result.get('data', {}).get('title') or result.get('data', {}).get('name')}")
        return result
    
    def _extract_company_data(self, message: str) -> Dict:
        """Extract company details from message"""
        data = {}
        # Extract company name - more flexible patterns
        patterns = [
            r'company\s+(?:named\s+|called\s+)?["\']?([A-Z][A-Za-z0-9\s&,\.\-]+?)["\']?(?:\s*in|\s*$|\s*with|\s*from)',
            r'create\s+["\']?([A-Z][A-Za-z0-9\s&,\.\-]+?)["\']?(?:\s*company|\s*$)',
            r'add\s+["\']?([A-Z][A-Za-z0-9\s&,\.\-]+?)["\']?(?:\s*company|\s*to)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                data['name'] = match.group(1).strip()
                break
        
        # If no pattern matched, try to extract any capitalized phrase
        if not data.get('name'):
            # Look for capitalized words after "company" or at start
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ['company', 'organization', 'create', 'add']:
                    # Get next 1-4 capitalized words
                    name_parts = []
                    for j in range(i+1, min(i+5, len(words))):
                        if words[j][0].isupper() or words[j].lower() in ['and', '&']:
                            name_parts.append(words[j])
                        else:
                            break
                    if name_parts:
                        data['name'] = ' '.join(name_parts)
                        break
        
        # Extract industry
        industries = ['technology', 'tech', 'finance', 'financial', 'healthcare', 'medical', 'retail', 'manufacturing', 'education', 'consulting', 'software', 'saas']
        for industry in industries:
            if industry in message.lower():
                data['industry'] = industry
                break
        
        return data
    
    def _extract_contact_data(self, message: str) -> Dict:
        """Extract contact details from message"""
        data = {}
        # Extract name
        patterns = [
            r'contact\s+(?:named\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'create\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                data['name'] = match.group(1).strip()
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            data['email'] = emails[0]
        
        # Extract company
        company_match = re.search(r'(?:at|from|for)\s+([A-Z][A-Za-z\s&]+?)(?:\s*$|\s*with)', message)
        if company_match:
            data['company'] = company_match.group(1).strip()
        
        # Extract title
        title_match = re.search(r'(?:title|role|position)\s+([A-Za-z\s]+)', message, re.IGNORECASE)
        if title_match:
            data['title'] = title_match.group(1).strip()
        
        return data
    
    def _extract_deal_data(self, message: str) -> Dict:
        """Extract deal details from message"""
        data = {}
        # Extract title - improved patterns
        patterns = [
            r'(?:create|add|new)\s+deal\s+["\']?([A-Za-z0-9\s-]+?)["\']?(?:\s+for|\s+worth|\s*$)',  # "create deal TITLE"
            r'deal\s+(?:named\s+|called\s+)?["\']?([A-Za-z0-9\s-]+?)["\']?(?:\s+for|\s+worth|\s*$)',  # "deal named TITLE"
            r'(?:create|add)\s+["\']?([A-Za-z0-9\s-]+?)["\']?\s+deal(?:\s+for|\s+worth|\s*$)',  # "create TITLE deal"
            r'opportunity\s+["\']?([A-Za-z0-9\s-]+?)["\']?(?:\s+for|\s+worth|\s*$)',  # "opportunity TITLE"
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Remove common filler words
                title = re.sub(r'^(a|an|the)\s+', '', title, flags=re.IGNORECASE)
                if len(title) > 2:  # Valid title
                    data['title'] = title
                    break
        
        # If no pattern matched, try to extract capitalized phrase after deal/opportunity
        if not data.get('title'):
            words = message.split()
            for i, word in enumerate(words):
                if word.lower() in ['deal', 'opportunity']:
                    # Get next 2-5 capitalized words
                    title_parts = []
                    for j in range(i+1, min(i+6, len(words))):
                        if words[j][0].isupper() or words[j].lower() in ['and', '&', '-']:
                            title_parts.append(words[j])
                        elif '$' in words[j] or words[j].lower() in ['for', 'worth']:
                            break
                    if title_parts:
                        data['title'] = ' '.join(title_parts)
                        break
        
        # Extract value
        value_patterns = [
            r'\$\s*([0-9,]+)',
            r'(?:worth|value|for)\s+\$?([0-9,]+)',
        ]
        for pattern in value_patterns:
            match = re.search(pattern, message)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    data['value'] = float(value_str)
                except:
                    pass
                break
        
        return data
    
    def _extract_task_data(self, message: str) -> Dict:
        """Extract task details from message"""
        data = {}
        # Extract task title
        patterns = [
            r'(?:create|add|new)\s+task\s+(.+?)(?:\s+(?:for|with|by|due)\s+|$)',  # "create task TITLE"
            r'task\s+["\']?([^"\']+?)["\']?(?:\s*$|\s+for)',  # "task TITLE"
            r'create\s+["\']?(.+?)["\']?\s+task',  # "create TITLE task"
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up common words
                title = re.sub(r'^(a|an|the)\s+', '', title, flags=re.IGNORECASE)
                data['title'] = title
                break
        
        return data
    
    def _extract_interaction_data(self, message: str) -> Dict:
        """Extract interaction details from message"""
        data = {}
        message_lower = message.lower()
        
        # Detect interaction type
        if 'call' in message_lower:
            data['type'] = 'call'
        elif 'email' in message_lower:
            data['type'] = 'email'
        elif 'meeting' in message_lower:
            data['type'] = 'meeting'
        else:
            data['type'] = 'note'
        
        data['notes'] = message
        return data
    
    def _extract_name(self, message: str) -> Optional[str]:
        """Extract person/company name from message"""
        patterns = [
            r'(?:delete|remove)\s+(?:contact|customer|company)\s+(.+?)(?:\s*$|,|\s+from)',  # More flexible
            r'(?:named|called)\s+(.+?)(?:\s*$|,)',
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Remove common words
                name = re.sub(r'^(the|a|an)\s+', '', name, flags=re.IGNORECASE)
                return name
        return None
    
    def _extract_deal_title(self, message: str) -> Optional[str]:
        """Extract deal title from message"""
        patterns = [
            r'deal\s+["\']?([^"\']+?)["\']?',
            r'opportunity\s+["\']?([^"\']+?)["\']?',
        ]
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(1).strip()
        return None

