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
        
        # Customer creation patterns
        customer_keywords = ['create customer', 'add customer', 'new customer', 'customer named']
        if any(keyword in message_lower for keyword in customer_keywords):
            extracted_data = self._extract_customer_data_fallback(message)
            
            # Build response based on what was extracted
            parts = []
            if extracted_data.get('name'):
                parts.append(f"named {extracted_data['name']}")
            if extracted_data.get('company'):
                parts.append(f"from {extracted_data['company']}")
            if extracted_data.get('email'):
                parts.append(f"with email {extracted_data['email']}")
            
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
        
        # Quick check for simple one-word greetings (instant response)
        for greeting, response in self.quick_greetings.items():
            if message_lower == greeting or message_lower == greeting + '?':
                return {
                    'message': response,
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
        """
        message_lower = message.lower()
        
        # Check for customer creation
        if any(keyword in message_lower for keyword in ['create customer', 'add customer', 'new customer', 'customer named']):
            extracted_data = self._extract_customer_data_fallback(message)
            return {
                'intent': 'add_customer',
                'action': 'add_customer',
                'extracted_data': extracted_data,
                'response': f"I'll create a customer with the information you provided."
            }
        
        # Check for CRM questions
        if any(keyword in message_lower for keyword in ['what is crm', 'explain crm', 'tell me about crm']):
            return {
                'intent': 'question_about_crm',
                'action': None,
                'extracted_data': {},
                'response': "CRM stands for Customer Relationship Management. It's a system that helps businesses manage customer interactions, track leads, automate workflows, and make data-driven decisions to increase sales!"
            }
        
        # Check for pricing questions
        if any(keyword in message_lower for keyword in ['price', 'cost', 'pricing', 'how much']):
            return {
                'intent': 'pricing',
                'action': None,
                'extracted_data': {},
                'response': "I'd be happy to discuss our pricing options! Our CRM offers flexible plans based on your team size and needs. Would you like to schedule a call with our sales team?"
            }
        
        # Default response
        return {
            'intent': 'general',
            'action': None,
            'extracted_data': {},
            'response': "I'm here to help! I can assist you with creating customers, answering questions about CRM, or connecting you with our team. What would you like to know?"
        }
    
    def _extract_customer_data_fallback(self, message: str) -> Dict:
        """
        Extract customer data using pattern matching (fallback method)
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
        
        # Extract name (look for "named X" or "customer X")
        name_patterns = [
            r'(?:named|called)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'customer\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, message)
            if match:
                extracted['name'] = match.group(1).strip()
                break
        
        # Extract company (look for "from X" or "company X")
        company_patterns = [
            r'from\s+([A-Z][A-Za-z\s&]+?)(?:\s*,|\s+email|\s+contact|$)',
            r'company[:\s]+([A-Z][A-Za-z\s&]+?)(?:\s*,|\s+email|$)',
        ]
        for pattern in company_patterns:
            match = re.search(pattern, message)
            if match:
                extracted['company'] = match.group(1).strip()
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
