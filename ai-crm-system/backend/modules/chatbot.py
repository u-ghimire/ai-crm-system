# modules/chatbot.py
"""
Chatbot Module - AI-powered conversational interface for customer queries
Handles basic customer service and information gathering
"""

import os
import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai

class ChatBot:
    def __init__(self):
        """Initialize chatbot with AI capabilities"""
        # PLACEHOLDER: Replace with your actual OpenAI API key
        self.api_key = os.environ.get('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')
        openai.api_key = self.api_key
        self.model = "gpt-3.5-turbo"
        
        # Define intents and responses
        self.intents = {
            'greeting': {
                'patterns': ['hello', 'hi', 'hey', 'good morning', 'good afternoon'],
                'responses': [
                    "Hello! How can I assist you today?",
                    "Hi there! What can I help you with?",
                    "Welcome! How may I help you?"
                ]
            },
            'pricing': {
                'patterns': ['price', 'cost', 'how much', 'pricing', 'quote', 'expensive'],
                'responses': [
                    "I'd be happy to discuss our pricing options. Could you tell me more about your specific needs?",
                    "Our pricing varies based on your requirements. What features are most important to you?",
                    "Let me connect you with our sales team for detailed pricing information."
                ]
            },
            'product_info': {
                'patterns': ['features', 'what can', 'capabilities', 'benefits', 'how does'],
                'responses': [
                    "Our CRM system offers comprehensive customer management, AI-powered insights, and workflow automation.",
                    "I can tell you about our key features: lead scoring, sales forecasting, and automated follow-ups.",
                    "Our solution helps you manage customers, track interactions, and improve sales processes."
                ]
            },
            'support': {
                'patterns': ['help', 'support', 'issue', 'problem', 'not working', 'error'],
                'responses': [
                    "I'm here to help! Can you describe the issue you're experiencing?",
                    "Let me assist you with that. What specific problem are you facing?",
                    "I'll do my best to help. Please provide more details about the issue."
                ]
            },
            'demo': {
                'patterns': ['demo', 'trial', 'try', 'test', 'see it'],
                'responses': [
                    "I'd love to schedule a demo for you! When would be a convenient time?",
                    "We offer personalized demos. Can I get your contact information to arrange one?",
                    "A demo is a great way to see our CRM in action. Let me connect you with our team."
                ]
            },
            'contact': {
                'patterns': ['contact', 'email', 'phone', 'reach', 'speak to'],
                'responses': [
                    "You can reach our team at sales@crmcompany.com or call 1-800-CRM-HELP.",
                    "I can connect you with the right person. What's the nature of your inquiry?",
                    "Our team is available Mon-Fri 9AM-6PM. How would you prefer to be contacted?"
                ]
            }
        }
        
        # Conversation context storage
        self.conversation_history = {}
    
    def process_message(self, message: str, context: Dict = None) -> Dict:
        """
        Process incoming message and generate response
        """
        # Store context for personalization
        customer_context = context or {}
        
        # Detect intent
        intent = self._detect_intent(message)
        
        # Check if we can use AI for a more sophisticated response
        if self._should_use_ai(message, intent):
            response = self._generate_ai_response(message, customer_context)
        else:
            response = self._generate_rule_response(message, intent, customer_context)
        
        # Extract any data from the message
        extracted_data = self._extract_information(message)
        
        # Determine next action
        next_action = self._determine_next_action(message, intent)
        
        return {
            'message': response,
            'intent': intent,
            'extracted_data': extracted_data,
            'next_action': next_action,
            'timestamp': datetime.now().isoformat()
        }
    
    def _detect_intent(self, message: str) -> str:
        """Detect the intent of the message"""
        message_lower = message.lower()
        
        for intent_name, intent_data in self.intents.items():
            for pattern in intent_data['patterns']:
                if pattern in message_lower:
                    return intent_name
        
        # If no specific intent detected, check for questions
        if '?' in message:
            return 'question'
        
        return 'general'
    
    def _should_use_ai(self, message: str, intent: str) -> bool:
        """Determine if AI response is needed"""
        # Use AI for complex questions or when no clear intent
        if intent in ['question', 'general']:
            return True
        
        # Use AI for longer messages that might need understanding
        if len(message.split()) > 10:
            return True
        
        # Use AI if message contains specific keywords
        ai_triggers = ['explain', 'how', 'why', 'what if', 'compare', 'difference']
        if any(trigger in message.lower() for trigger in ai_triggers):
            return True
        
        return False
    
    def _generate_ai_response(self, message: str, context: Dict) -> str:
        """Generate AI-powered response"""
        try:
            # Build context for the AI
            system_prompt = """You are a helpful CRM chatbot assistant. You help customers with:
            1. Product information and features
            2. Pricing inquiries
            3. Technical support
            4. Scheduling demos
            5. General customer service
            
            Be professional, friendly, and concise. If you don't know something, offer to connect them with a human agent."""
            
            # Add customer context if available
            if context:
                customer_info = f"\nCustomer Info: {context.get('name', 'Guest')} from {context.get('company', 'Unknown Company')}"
                if context.get('status'):
                    customer_info += f", Status: {context['status']}"
                system_prompt += customer_info
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message['content'].strip()
            
        except Exception as e:
            print(f"AI Chatbot Error: {e}")
            return self._get_fallback_response(message)
    
    def _generate_rule_response(self, message: str, intent: str, context: Dict) -> str:
        """Generate rule-based response"""
        import random
        
        if intent in self.intents:
            responses = self.intents[intent]['responses']
            base_response = random.choice(responses)
            
            # Personalize if we have context
            if context and context.get('name'):
                base_response = f"Hello {context['name']}! " + base_response
            
            return base_response
        
        return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message: str) -> str:
        """Provide fallback response"""
        fallback_responses = [
            "I understand you're asking about our CRM. Could you be more specific?",
            "That's a great question! Let me connect you with our team for a detailed answer.",
            "I'd like to help you better. Could you provide more details?",
            "Thank you for your interest. How can I assist you with our CRM solution?"
        ]
        
        import random
        return random.choice(fallback_responses)
    
    def _extract_information(self, message: str) -> Dict:
        """Extract structured information from message"""
        extracted = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            extracted['email'] = emails[0]
        
        # Extract phone number
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{4,6}'
        phones = re.findall(phone_pattern, message)
        if phones:
            extracted['phone'] = phones[0]
        
        # Extract company name (simple heuristic)
        company_indicators = ['work at', 'from', 'company', 'representing']
        for indicator in company_indicators:
            if indicator in message.lower():
                parts = message.lower().split(indicator)
                if len(parts) > 1:
                    company_part = parts[1].strip().split()[0:3]  # Take next 1-3 words
                    extracted['company'] = ' '.join(company_part).title()
                    break
        
        # Extract budget mentions
        budget_pattern = r'\$[\d,]+\.?\d*[kKmM]?'
        budgets = re.findall(budget_pattern, message)
        if budgets:
            extracted['budget'] = budgets[0]
        
        # Extract timeline
        timeline_keywords = {
            'immediately': 'immediate',
            'asap': 'immediate',
            'urgent': 'immediate',
            'this week': '1_week',
            'next week': '1_week',
            'this month': '1_month',
            'next month': '1_month',
            'quarter': '3_months',
            'year': '1_year'
        }
        
        message_lower = message.lower()
        for keyword, timeline in timeline_keywords.items():
            if keyword in message_lower:
                extracted['timeline'] = timeline
                break
        
        return extracted
    
    def _determine_next_action(self, message: str, intent: str) -> str:
        """Determine the next action based on conversation"""
        if intent == 'demo':
            return 'schedule_demo'
        elif intent == 'pricing':
            return 'send_pricing_info'
        elif intent == 'support':
            return 'create_ticket'
        elif intent == 'contact':
            return 'forward_to_sales'
        elif 'interested' in message.lower() or 'sign up' in message.lower():
            return 'qualify_lead'
        else:
            return 'continue_conversation'
    
    def handle_conversation_flow(self, session_id: str, message: str, context: Dict = None) -> Dict:
        """Handle multi-turn conversations with context"""
        # Initialize or get conversation history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        # Add current message to history
        self.conversation_history[session_id].append({
            'role': 'user',
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process message
        response = self.process_message(message, context)
        
        # Add response to history
        self.conversation_history[session_id].append({
            'role': 'assistant',
            'message': response['message'],
            'timestamp': response['timestamp']
        })
        
        # Keep only last 10 messages to manage memory
        if len(self.conversation_history[session_id]) > 20:
            self.conversation_history[session_id] = self.conversation_history[session_id][-20:]
        
        return response
    
    def get_suggested_responses(self, intent: str) -> List[str]:
        """Get suggested quick responses for users"""
        suggestions = {
            'greeting': [
                "Tell me about your CRM",
                "I need help with customer management",
                "Schedule a demo"
            ],
            'pricing': [
                "What's included in the basic plan?",
                "Do you offer custom pricing?",
                "Can I get a free trial?"
            ],
            'product_info': [
                "How does lead scoring work?",
                "Can it integrate with my tools?",
                "Show me the AI features"
            ],
            'support': [
                "I can't log in",
                "How do I import contacts?",
                "I need technical support"
            ],
            'demo': [
                "I'm available this week",
                "Send me more information first",
                "What should I prepare for the demo?"
            ],
            'general': [
                "Tell me more",
                "How can you help my business?",
                "What makes you different?"
            ]
        }
        
        return suggestions.get(intent, suggestions['general'])
    
    def qualify_lead(self, conversation_data: List[Dict]) -> Dict:
        """Analyze conversation to qualify lead"""
        qualification = {
            'is_qualified': False,
            'score': 0,
            'missing_info': [],
            'strengths': [],
            'next_steps': []
        }
        
        # Check what information we have
        has_contact = False
        has_budget = False
        has_timeline = False
        has_need = False
        
        for message in conversation_data:
            if message.get('extracted_data'):
                data = message['extracted_data']
                if data.get('email') or data.get('phone'):
                    has_contact = True
                    qualification['strengths'].append('Provided contact information')
                if data.get('budget'):
                    has_budget = True
                    qualification['strengths'].append('Has defined budget')
                if data.get('timeline'):
                    has_timeline = True
                    qualification['strengths'].append('Has timeline for decision')
        
        # Check for need indicators
        need_keywords = ['need', 'looking for', 'interested', 'problem', 'solution', 'help']
        for message in conversation_data:
            if message.get('role') == 'user':
                if any(keyword in message.get('message', '').lower() for keyword in need_keywords):
                    has_need = True
                    qualification['strengths'].append('Expressed clear need')
                    break
        
        # Calculate qualification score
        score = 0
        score += 30 if has_contact else 0
        score += 25 if has_budget else 0
        score += 20 if has_timeline else 0
        score += 25 if has_need else 0
        
        qualification['score'] = score
        qualification['is_qualified'] = score >= 50
        
        # Identify missing information
        if not has_contact:
            qualification['missing_info'].append('Contact information')
            qualification['next_steps'].append('Collect email and phone number')
        if not has_budget:
            qualification['missing_info'].append('Budget range')
            qualification['next_steps'].append('Discuss budget expectations')
        if not has_timeline:
            qualification['missing_info'].append('Decision timeline')
            qualification['next_steps'].append('Understand implementation timeline')
        if not has_need:
            qualification['missing_info'].append('Specific needs')
            qualification['next_steps'].append('Explore pain points and requirements')
        
        # Add general next steps
        if qualification['is_qualified']:
            qualification['next_steps'].insert(0, 'Schedule product demo')
            qualification['next_steps'].insert(1, 'Assign to sales representative')
        else:
            qualification['next_steps'].insert(0, 'Continue nurturing')
        
        return qualification
    
    def generate_chat_summary(self, conversation_data: List[Dict]) -> str:
        """Generate summary of chat conversation"""
        if not conversation_data:
            return "No conversation data available."
        
        # Extract key points
        user_messages = [msg['message'] for msg in conversation_data if msg.get('role') == 'user']
        
        # Use AI to summarize if available
        try:
            conversation_text = "\n".join([f"{msg['role']}: {msg['message']}" for msg in conversation_data])
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Summarize this customer service conversation in 2-3 sentences, highlighting key points and any action items."},
                    {"role": "user", "content": conversation_text}
                ],
                max_tokens=100,
                temperature=0.5
            )
            
            return response.choices[0].message['content'].strip()
            
        except:
            # Fallback to simple summary
            topics = []
            for intent in ['pricing', 'demo', 'support', 'product_info']:
                if any(intent in msg.get('intent', '') for msg in conversation_data):
                    topics.append(intent)
            
            summary = f"Customer engaged in conversation about: {', '.join(topics) if topics else 'general inquiry'}. "
            summary += f"Total messages: {len(conversation_data)}."
            
            return summary