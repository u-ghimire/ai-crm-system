# modules/chatbot.py
"""
Chatbot Module - AI-powered conversational interface
Uses Qwen AI for intelligent intent detection and entity extraction
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from .huggingface_ai import HuggingFaceAI

class ChatBot:
    def __init__(self, ai_model: HuggingFaceAI):
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
        
        # Customer creation patterns - enhanced with more variations
        customer_keywords = ['create customer', 'add customer', 'new customer', 'customer named',
                           'create a customer', 'add a customer', 'make a customer', 'register customer',
                           'customer called', 'customer for', 'want to add', 'need to create',
                           'create contact', 'add contact', 'new contact']
        
        if any(keyword in message_lower for keyword in customer_keywords):
            extracted_data = self._extract_customer_data_fallback(message)
            
            # Validate we extracted something meaningful
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
        """
        message_lower = message.lower().strip()
        
        # Flexible greeting detection (substring matching)
        greeting_keywords = ['hi', 'hello', 'hey', 'how are you', 'good morning', 'good afternoon', 
                           'good evening', 'howdy', 'greetings', 'what\'s up', 'whats up', 'sup']
        
        # Check if message is a greeting (flexible matching)
        is_greeting = any(
            keyword in message_lower and len(message_lower) < 50  # Short messages only
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
            # Get AI analysis with shorter max length for speed
            ai_response = self.ai_model.generate(prompt, max_length=150)
            
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
            else:
                response_text = "I'll create a customer with the information you provided."
            
            return {
                'intent': 'add_customer',
                'action': 'add_customer',
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
        
        # Default response for unrecognized input
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
    
    def extract_customer_data(self, message: str) -> Dict:
        """
        Public method to extract customer data (used by app.py)
        """
        # Try AI analysis first
        analysis = self._analyze_with_ai(message)
        if analysis.get('extracted_data'):
            return analysis['extracted_data']
        
        # Fallback to pattern matching
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
            summary += self.ai_model.generate(prompt, max_length=100)
        
        return summary
