# modules/chatbot.py
"""
Chatbot Module - AI-powered conversational interface
Uses Qwen AI for intelligent intent detection and entity extraction
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .groq_ai import GroqAI

class ChatBot:
    def __init__(self, ai_model: GroqAI):
        """Initialize chatbot with AI capabilities"""
        self.ai_model = ai_model
        
        # Quick responses for simple greetings (no AI needed - instant)
        self.quick_greetings = {
            'hi': "Hi there! How can I help you today?",
            'hello': "Hello! What can I assist you with?",
            'hey': "Hey! How may I help you?",
            'how are you': "I'm doing great, thank you! How can I assist you today?",
            'good morning': "Good morning! What can I help you with?",
            'good afternoon': "Good afternoon! How may I assist you?"
        }
        
        # Conversation context storage
        self.conversation_history = {}
    
    def _quick_pattern_check(self, message: str) -> Optional[Dict]:
        """
        Quick pattern-based check for common intents (instant, no AI needed)
        Returns None if AI analysis is needed
        """
        message_lower = message.lower().strip()
        
        # ==================== CUSTOMER CREATION ====================
        customer_keywords = ['create customer', 'add customer', 'new customer', 'customer named',
                           'create a customer', 'add a customer', 'make a customer', 'register customer',
                           'customer called', 'customer for', 'want to add', 'need to create',
                           'create contact', 'add contact', 'new contact']
        
        if any(keyword in message_lower for keyword in customer_keywords):
            extracted_data = self._extract_customer_data_fallback(message)
            
            # Check if we extracted meaningful data
            has_data = any([
                extracted_data.get('name'),
                extracted_data.get('email'),
                extracted_data.get('company'),
                extracted_data.get('phone')
            ])
            
            if has_data:
                # Build response based on what was extracted
                parts = []
                if extracted_data.get('name'):
                    parts.append(f"named {extracted_data['name']}")
                if extracted_data.get('company'):
                    parts.append(f"from {extracted_data['company']}")
                if extracted_data.get('email'):
                    parts.append(f"with email {extracted_data['email']}")
                if extracted_data.get('phone'):
                    parts.append(f"with phone {extracted_data['phone']}")
                
                response_text = "I'll create a customer " + " ".join(parts) + "!" if parts else "I'll create that customer for you!"
                
                return {
                    'intent': 'add_customer',
                    'action': 'add_customer',
                    'extracted_data': extracted_data,
                    'response': response_text
                }
            else:
                # No data extracted - ask for details instead of calling AI
                return {
                    'intent': 'add_customer_needs_info',
                    'action': None,
                    'extracted_data': {},
                    'response': "I'd be happy to create a customer! Please provide some details like:\n• Name (e.g., 'John Doe')\n• Company (e.g., 'Acme Corp')\n• Email (e.g., 'john@example.com')\n\nFor example: 'Create a customer named John Doe from Acme Corp with email john@acme.com'"
                }
        
        # ==================== SEND EMAIL ====================
        email_keywords = ['send email', 'email to', 'send message to', 'notify', 'contact customer',
                         'reach out to', 'send a message', 'email customer', 'email']
        
        if any(keyword in message_lower for keyword in email_keywords):
            # Check if this is the initial email request
            if 'to' not in message_lower and not any(char.isdigit() for char in message):
                # User just said "send email" without specifying recipient
                return {
                    'intent': 'send_email_start',
                    'action': 'send_email_ask_customer',
                    'extracted_data': {},
                    'response': "Sure! What is the name of the customer you'd like to email?"
                }
            
            # Extract customer name if mentioned
            email_data = self._extract_email_data(message)
            
            if email_data.get('customer_name'):
                return {
                    'intent': 'send_email_get_customer',
                    'action': 'send_email_lookup_customer',
                    'extracted_data': email_data,
                    'response': f"Looking up email for {email_data.get('customer_name')}..."
                }
            
            return {
                'intent': 'send_email',
                'action': 'send_email',
                'extracted_data': email_data,
                'response': f"I'll send an email to {email_data.get('recipient', 'the customer')}!"
            }
        
        # ==================== DELETE CUSTOMER ====================
        delete_keywords = ['delete customer', 'remove customer', 'delete contact', 'remove contact',
                          'delete a customer', 'remove a customer']
        
        if any(keyword in message_lower for keyword in delete_keywords):
            # Extract customer name if mentioned
            customer_name = None
            name_patterns = [
                r'(?:delete|remove)\s+(?:customer|contact)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'(?:customer|contact)\s+(?:named|called)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, message)
                if match:
                    customer_name = match.group(1).strip()
                    break
            
            if customer_name:
                return {
                    'intent': 'delete_customer_confirm',
                    'action': 'delete_customer_lookup',
                    'extracted_data': {'customer_name': customer_name},
                    'response': f"Looking up customer {customer_name}..."
                }
            else:
                # Ask for customer name
                return {
                    'intent': 'delete_customer_start',
                    'action': 'delete_customer_ask_name',
                    'extracted_data': {},
                    'response': "Which customer would you like to delete? Please provide their name."
                }
        
        # ==================== GET INSIGHTS ====================
        insight_keywords = ['insights', 'analyze', 'report', 'statistics', 'stats about',
                          'show me data', 'what are the trends', 'customer data', 'sales data',
                          'how many customers', 'top leads', 'forecast']
        
        if any(keyword in message_lower for keyword in insight_keywords):
            return {
                'intent': 'get_insights',
                'action': 'get_insights',
                'extracted_data': {'query': message},
                'response': "Let me analyze the data and provide insights..."
            }
        
        # CRM questions
        if any(keyword in message_lower for keyword in ['what is crm', 'explain crm', 'tell me about crm']):
            return {
                'intent': 'question_about_crm',
                'action': None,
                'extracted_data': {},
                'response': "CRM stands for Customer Relationship Management. It's a system that helps businesses manage customer interactions, track leads, automate workflows, and make data-driven decisions!"
            }
        
        # Pricing questions
        if any(keyword in message_lower for keyword in ['price', 'cost', 'pricing', 'how much']):
            return {
                'intent': 'pricing',
                'action': None,
                'extracted_data': {},
                'response': "I'd be happy to discuss our pricing! Our CRM offers flexible plans based on your team size. Would you like to schedule a call with our sales team?"
            }
        
        return None  # No quick match, need AI analysis
    
    def process_message(self, message: str, context: Dict = None) -> Dict:
        """
        Process incoming message using AI for intelligent understanding
        
        Args:
            message: The user's message
            context: Conversation context (e.g., {'in_conversation': True, 'waiting_for': 'customer_name'})
        """
        message_lower = message.lower().strip()
        
        # If we're in the middle of a conversation, don't treat input as greetings
        if context and context.get('in_conversation'):
            # Return the message as-is for context-aware processing
            return {
                'message': message,
                'intent': 'conversation_response',
                'action': None,
                'extracted_data': {'user_input': message},
                'timestamp': datetime.now().isoformat()
            }
        
        # Flexible greeting detection (substring matching) - only for standalone messages
        greeting_keywords = ['hi', 'hello', 'hey', 'how are you', 'good morning', 'good afternoon', 
                           'good evening', 'howdy', 'greetings', 'what\'s up', 'whats up', 'sup']
        
        # Check if message is a greeting - must be exact or very short
        is_greeting = False
        if len(message_lower) < 20:  # Only check short messages
            is_greeting = any(
                message_lower == keyword or 
                (message_lower.startswith(keyword) and len(message_lower) - len(keyword) <= 5)
                for keyword in greeting_keywords
            )
        
        if is_greeting:
            # Pick appropriate response based on greeting type
            if 'how are you' in message_lower:
                greeting_response = "I'm doing great, thank you! How can I assist you today?"
            elif 'morning' in message_lower:
                greeting_response = "Good morning! What can I help you with?"
            elif 'afternoon' in message_lower:
                greeting_response = "Good afternoon! How may I assist you?"
            elif 'evening' in message_lower:
                greeting_response = "Good evening! What can I do for you?"
            else:
                greeting_response = "Hello! How can I help you today?"
            
            return {
                'message': greeting_response,
                'intent': 'greeting',
                'action': None,
                'extracted_data': {},
                'timestamp': datetime.now().isoformat()
            }
        
        # Use AI to analyze the message intelligently
        analysis = self._analyze_with_ai(message)
        
        # Return the analysis result
        return {
            'message': analysis.get('response', "I'm here to help! What would you like to know?"),
            'intent': analysis.get('intent', 'unknown'),
            'action': analysis.get('action'),
            'extracted_data': analysis.get('extracted_data', {}),
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_with_ai(self, message: str) -> Dict:
        """
        Use Qwen AI to intelligently analyze message, detect intent, and extract data
        """
        # First, try quick pattern matching for common cases (faster)
        quick_result = self._quick_pattern_check(message)
        if quick_result:
            return quick_result
        
        # Only use AI for complex cases
        prompt = f"""Analyze: "{message}"
Respond ONLY with JSON:
{{"intent":"add_customer|question|greeting|general","action":"add_customer|null","name":"name or null","email":"email or null","company":"company or null","response":"brief response"}}"""
        
        try:
            # Get AI analysis with increased tokens for better responses
            ai_response = self.ai_model.generate(prompt, max_length=300)
            
            # Try to parse JSON from response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)
                
                # Convert flat JSON to expected format
                return {
                    'intent': result.get('intent', 'general'),
                    'action': result.get('action'),
                    'extracted_data': {
                        'name': result.get('name'),
                        'email': result.get('email'),
                        'company': result.get('company'),
                        'phone': result.get('phone')
                    },
                    'response': result.get('response', "I'm here to help!")
                }
            
            # Fallback: Pattern-based analysis
            return self._fallback_analysis(message)
            
        except Exception as e:
            print(f"Error in AI analysis: {e}")
            # Fallback to pattern matching
            return self._fallback_analysis(message)
    
    def _fallback_analysis(self, message: str) -> Dict:
        """
        Fallback pattern-based analysis if AI fails
        Enhanced to handle more natural language patterns
        """
        message_lower = message.lower()
        
        # Check for customer creation - expanded keyword list
        customer_creation_keywords = [
            'create customer', 'add customer', 'new customer', 'customer named',
            'create a customer', 'add a customer', 'make a customer', 'register customer',
            'customer called', 'customer for', 'want to add', 'need to create',
            'create contact', 'add contact', 'new contact', 'register contact'
        ]
        
        if any(keyword in message_lower for keyword in customer_creation_keywords):
            extracted_data = self._extract_customer_data_fallback(message)
            
            # Check if we extracted meaningful data
            has_data = any([
                extracted_data.get('name'),
                extracted_data.get('email'),
                extracted_data.get('company')
            ])
            
            if has_data:
                # Build detailed response
                parts = []
                if extracted_data.get('name'):
                    parts.append(f"Name: {extracted_data['name']}")
                if extracted_data.get('company'):
                    parts.append(f"Company: {extracted_data['company']}")
                if extracted_data.get('email'):
                    parts.append(f"Email: {extracted_data['email']}")
                if extracted_data.get('phone'):
                    parts.append(f"Phone: {extracted_data['phone']}")
                
                response_text = f"I'll create a customer with the following details: {', '.join(parts)}"
                action = 'add_customer'
            else:
                # No data - ask for details instead of creating empty customer
                response_text = "I'd be happy to create a customer! Please provide some details like:\n• Name (e.g., 'John Doe')\n• Company (e.g., 'Acme Corp')\n• Email (e.g., 'john@example.com')\n\nFor example: 'Create a customer named John Doe from Acme Corp with email john@acme.com'"
                action = None
            
            return {
                'intent': 'add_customer' if has_data else 'add_customer_needs_info',
                'action': action,
                'extracted_data': extracted_data,
                'response': response_text
            }
        
        # Check for CRM questions
        if any(keyword in message_lower for keyword in ['what is crm', 'explain crm', 'tell me about crm', 'about crm']):
            return {
                'intent': 'question_about_crm',
                'action': None,
                'extracted_data': {},
                'response': "CRM stands for Customer Relationship Management. It's a system that helps businesses manage customer interactions, track leads, automate workflows, and make data-driven decisions to increase sales!"
            }
        
        # Check for pricing questions
        if any(keyword in message_lower for keyword in ['price', 'cost', 'pricing', 'how much', 'payment', 'subscription']):
            return {
                'intent': 'pricing',
                'action': None,
                'extracted_data': {},
                'response': "I'd be happy to discuss our pricing options! Our CRM offers flexible plans based on your team size and needs. Would you like to schedule a call with our sales team?"
            }
        
        # Check for help/support questions
        if any(keyword in message_lower for keyword in ['help', 'support', 'assist', 'can you help']):
            return {
                'intent': 'help',
                'action': None,
                'extracted_data': {},
                'response': "I'm here to help! I can assist you with:\n• Creating customers and contacts\n• Answering questions about our CRM\n• Providing pricing information\n• Connecting you with our team\n\nWhat would you like to do?"
            }
        
        # Default: Use AI for unrecognized input (intelligent fallback)
        try:
            # Use Groq AI for natural, intelligent responses
            prompt = f"""You are a helpful CRM assistant. The user asked: "{message}"

Respond naturally and helpfully. If it's a general question, answer it. If it's about CRM/sales/business, provide relevant insights. If you can't answer (like weather), politely explain you're a CRM assistant.

Keep response under 100 words."""
            
            ai_response = self.ai_model.generate(prompt, max_length=200)
            
            # Clean up any thinking tags
            ai_response = re.sub(r'<think>.*?</think>', '', ai_response, flags=re.DOTALL).strip()
            
            return {
                'intent': 'general_ai',
                'action': None,
                'extracted_data': {},
                'response': ai_response if ai_response else "I'm here to help! I can assist you with creating customers, answering questions about CRM, or connecting you with our team. What would you like to know?"
            }
        except Exception as e:
            print(f"AI fallback error: {e}")
            return {
                'intent': 'general',
                'action': None,
                'extracted_data': {},
                'response': "I'm here to help! I can assist you with creating customers, answering questions about CRM, or connecting you with our team. What would you like to know?"
            }
    
    def _extract_customer_data_fallback(self, message: str) -> Dict:
        """
        Extract customer data using pattern matching (fallback method)
        Enhanced to handle more natural language variations
        """
        extracted = {}
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            extracted['email'] = emails[0]
        
        # Extract phone
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        phones = re.findall(phone_pattern, message)
        if phones:
            extracted['phone'] = phones[0]
        
        # Extract name - enhanced patterns
        name_patterns = [
            r'(?:named|called)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'customer\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'(?:name\s+is|name:\s*)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:add|create)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # "create John Doe"
            r'customer\s+for\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "customer for John Doe"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, message)
            if match:
                extracted['name'] = match.group(1).strip()
                break
        
        # Extract company - enhanced patterns
        company_patterns = [
            r'from\s+([A-Z][A-Za-z\s&,\.]+?)(?:\s*with|\s*contact|\s*email|\s*phone|$)',
            r'company[:\s]+([A-Z][A-Za-z\s&,\.]+?)(?:\s*with|\s*contact|\s*email|$)',
            r'at\s+([A-Z][A-Za-z\s&,\.]+?)(?:\s*with|\s*contact|\s*email|$)',
            r'works?\s+(?:at|for)\s+([A-Z][A-Za-z\s&,\.]+?)(?:\s*with|\s*contact|\s*email|$)',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, message)
            if match:
                company = match.group(1).strip()
                # Clean up company name (remove trailing punctuation)
                company = re.sub(r'[,\.]$', '', company).strip()
                # Validate it's not too long or contains weird characters
                if len(company) < 50 and not re.search(r'[<>{}]', company):
                    extracted['company'] = company
                    break
        
        return extracted
    
    def _extract_email_data(self, message: str) -> Dict:
        """
        Extract email recipient and content from message
        """
        extracted = {'recipient': None, 'customer_name': None, 'subject': 'CRM Email', 'body': None}
        
        # Extract email address
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, message)
        if emails:
            extracted['recipient'] = emails[0]
        
        # Extract customer name patterns (e.g., "send email to John Doe" or just "John Doe")
        name_patterns = [
            r'(?:email|send|notify|contact|to)\s+(?:to\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(?:customer|client)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)$',  # Just a name by itself
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, message)
            if match:
                name = match.group(1).strip()
                # Validate it's a reasonable name
                if 2 < len(name) < 50 and not any(word in name.lower() for word in ['email', 'send', 'message']):
                    extracted['customer_name'] = name
                    break
        
        # Extract subject if mentioned
        if 'subject:' in message.lower():
            subject_match = re.search(r'subject:\s*([^\n]+)', message, re.IGNORECASE)
            if subject_match:
                extracted['subject'] = subject_match.group(1).strip()
        
        # The message content could be the body
        extracted['body'] = message
        
        return extracted
        for pattern in name_patterns:
            match = re.search(pattern, message)
            if match:
                if not extracted['recipient']:  # Only if we don't have an email
                    extracted['recipient'] = match.group(1).strip()
                break
        
        # Extract subject if mentioned
        if 'subject:' in message.lower():
            subject_match = re.search(r'subject:\s*([^\n]+)', message, re.IGNORECASE)
            if subject_match:
                extracted['subject'] = subject_match.group(1).strip()
        
        # The rest of the message can be the body (simplified)
        extracted['body'] = message
        
        return extracted
    
    def extract_customer_data(self, message: str) -> Dict:
        """
        Public method to extract customer data (used by app.py)
        ALWAYS uses fast pattern matching - NEVER calls AI to avoid timeouts
        """
        # Use pattern matching directly - fast and reliable
        return self._extract_customer_data_fallback(message)
    
    def _determine_next_action(self, message: str, intent: str) -> Optional[str]:
        """Determine if any follow-up action is needed"""
        if intent == 'add_customer':
            return 'add_customer'
        elif intent == 'demo':
            return 'schedule_demo'
        elif intent == 'support':
            return 'create_ticket'
        return None
    
    def get_conversation_summary(self, customer_id: str) -> str:
        """Generate a summary of the conversation"""
        if customer_id not in self.conversation_history:
            return "No conversation history available."
        
        history = self.conversation_history[customer_id]
        summary = f"Conversation with customer {customer_id}:\n"
        summary += f"Total messages: {len(history)}\n"
        
        # Use AI to summarize if we have significant history
        if len(history) > 3:
            messages_text = "\n".join([f"- {msg['message']}" for msg in history[-10:]])
            prompt = f"Summarize this customer conversation:\n{messages_text}\n\nSummary:"
            summary += self.ai_model.generate(prompt, max_length=200)
        
        return summary
