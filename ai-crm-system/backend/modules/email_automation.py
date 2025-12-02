"""
Email Automation Module
Handles email drafting, personalized templates, sentiment analysis, and tone-aware generation
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import re
from modules.groq_ai import GroqAI
from modules import db_helper

class EmailAutomation:
    def __init__(self):
        self.groq_ai = GroqAI()
        
        # Predefined tone styles
        self.tone_styles = {
            'professional': 'formal, business-appropriate, respectful',
            'friendly': 'warm, approachable, conversational yet professional',
            'urgent': 'direct, action-oriented, time-sensitive',
            'persuasive': 'compelling, benefit-focused, motivating',
            'apologetic': 'empathetic, understanding, solution-oriented',
            'follow-up': 'polite, gentle reminder, value-adding'
        }
    
    def draft_email(self, intent: str, recipient_data: Dict[str, Any], 
                   tone: str = 'professional', context: str = '') -> Dict[str, Any]:
        """
        Draft an email based on intent, recipient data, and desired tone
        
        Args:
            intent: Purpose of email (follow_up, proposal, introduction, etc.)
            recipient_data: Dict with name, company, previous_interactions, etc.
            tone: Desired tone (professional, friendly, urgent, etc.)
            context: Additional context or specific points to include
        """
        try:
            # Get recipient history for personalization
            interaction_history = self._get_recipient_history(recipient_data.get('customer_id'))
            
            # Build personalization context
            personalization = self._build_personalization_context(
                recipient_data, 
                interaction_history
            )
            
            # Get tone description
            tone_desc = self.tone_styles.get(tone, self.tone_styles['professional'])
            
            prompt = f"""
Draft a professional email with the following details:

INTENT: {intent}
TONE: {tone_desc}
RECIPIENT: {recipient_data.get('name', 'Valued Customer')}
COMPANY: {recipient_data.get('company', '')}
POSITION: {recipient_data.get('job_title', '')}

PERSONALIZATION CONTEXT:
{personalization}

ADDITIONAL CONTEXT:
{context}

Generate a complete email with:
1. Compelling subject line
2. Personalized greeting
3. Well-structured body (2-3 paragraphs)
4. Clear call-to-action
5. Professional closing

Format as:
SUBJECT: [subject line]

BODY:
[email body]

SIGNATURE:
[professional closing]
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=600)
            
            # Parse response
            subject = self._extract_section(response, 'SUBJECT:')
            body = self._extract_section(response, 'BODY:')
            signature = self._extract_section(response, 'SIGNATURE:')
            
            return {
                'success': True,
                'subject': subject,
                'body': body,
                'signature': signature,
                'full_email': f"{body}\n\n{signature}",
                'tone': tone,
                'personalized': bool(personalization)
            }
            
        except Exception as e:
            print(f"Error drafting email: {e}")
            return {
                'success': False,
                'message': f"Failed to draft email: {str(e)}"
            }
    
    def generate_outreach_template(self, lead_data: Dict[str, Any], 
                                  campaign_type: str = 'cold_outreach') -> Dict[str, Any]:
        """
        Generate personalized outreach template based on lead behavior and data
        
        Args:
            lead_data: Lead information including behavior patterns
            campaign_type: Type of campaign (cold_outreach, warm_lead, reengagement)
        """
        try:
            # Analyze lead behavior
            behavior_analysis = self._analyze_lead_behavior(lead_data)
            
            prompt = f"""
Create a personalized outreach email template for:

CAMPAIGN TYPE: {campaign_type}
LEAD PROFILE:
- Name: {lead_data.get('name')}
- Company: {lead_data.get('company')}
- Industry: {lead_data.get('industry')}
- Job Title: {lead_data.get('job_title')}
- Source: {lead_data.get('source')}
- Lead Score: {lead_data.get('lead_score', 0)}

BEHAVIOR ANALYSIS:
{behavior_analysis}

Generate a highly personalized template that:
1. References specific pain points for their industry
2. Shows understanding of their business context
3. Provides clear value proposition
4. Includes a low-friction call-to-action
5. Can be easily customized for similar leads

Include [PERSONALIZATION_TOKENS] where manual customization should occur.
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=700)
            
            # Extract template components
            subject_templates = self._extract_template_variations(response, 'subject')
            body_template = self._clean_template(response)
            
            return {
                'success': True,
                'template_id': f"{campaign_type}_{datetime.now().strftime('%Y%m%d')}",
                'campaign_type': campaign_type,
                'subject_variations': subject_templates,
                'body_template': body_template,
                'personalization_tokens': self._extract_tokens(body_template),
                'recommended_for': behavior_analysis
            }
            
        except Exception as e:
            print(f"Error generating template: {e}")
            return {
                'success': False,
                'message': f"Failed to generate template: {str(e)}"
            }
    
    def analyze_sentiment(self, message: str, context: str = '') -> Dict[str, Any]:
        """
        Analyze sentiment of customer message to guide response tone
        
        Returns sentiment score, emotion, urgency level, and recommended response approach
        """
        try:
            prompt = f"""
Analyze the sentiment and emotion in this customer message:

MESSAGE: "{message}"

CONTEXT: {context}

Provide a detailed analysis in this format:
SENTIMENT: positive/negative/neutral (score: 0-100)
EMOTION: primary emotion detected
URGENCY: low/medium/high
CONCERNS: list any concerns or pain points
RECOMMENDED_TONE: how to respond
RESPONSE_APPROACH: key points for response strategy
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=400)
            
            # Parse response
            sentiment_line = self._extract_section(response, 'SENTIMENT:')
            sentiment_type = 'neutral'
            sentiment_score = 50
            
            if 'positive' in sentiment_line.lower():
                sentiment_type = 'positive'
                score_match = re.search(r'(\d+)', sentiment_line)
                sentiment_score = int(score_match.group(1)) if score_match else 75
            elif 'negative' in sentiment_line.lower():
                sentiment_type = 'negative'
                score_match = re.search(r'(\d+)', sentiment_line)
                sentiment_score = int(score_match.group(1)) if score_match else 25
            else:
                score_match = re.search(r'(\d+)', sentiment_line)
                sentiment_score = int(score_match.group(1)) if score_match else 50
            
            emotion = self._extract_section(response, 'EMOTION:')
            urgency = self._extract_section(response, 'URGENCY:')
            concerns = self._extract_section(response, 'CONCERNS:')
            recommended_tone = self._extract_section(response, 'RECOMMENDED_TONE:')
            response_approach = self._extract_section(response, 'RESPONSE_APPROACH:')
            
            return {
                'success': True,
                'sentiment': {
                    'type': sentiment_type,
                    'score': sentiment_score,
                    'emotion': emotion.strip()
                },
                'urgency': urgency.strip().lower(),
                'concerns': [c.strip() for c in concerns.split('\n') if c.strip()],
                'recommended_tone': recommended_tone.strip(),
                'response_approach': response_approach.strip(),
                'requires_immediate_attention': urgency.strip().lower() == 'high' or sentiment_score < 30
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'success': False,
                'message': f"Failed to analyze sentiment: {str(e)}"
            }
    
    def generate_response_to_message(self, customer_message: str, 
                                    customer_data: Dict[str, Any],
                                    sentiment_analysis: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate intelligent response to customer message based on sentiment analysis
        """
        try:
            # Analyze sentiment if not provided
            if not sentiment_analysis:
                sentiment_analysis = self.analyze_sentiment(customer_message)
            
            # Determine appropriate tone
            if sentiment_analysis.get('sentiment', {}).get('type') == 'negative':
                tone = 'apologetic'
            elif sentiment_analysis.get('urgency') == 'high':
                tone = 'urgent'
            elif sentiment_analysis.get('sentiment', {}).get('score', 50) > 70:
                tone = 'friendly'
            else:
                tone = 'professional'
            
            # Get customer history
            interaction_history = self._get_recipient_history(customer_data.get('customer_id'))
            
            prompt = f"""
Generate a response to this customer message:

CUSTOMER MESSAGE: "{customer_message}"

CUSTOMER INFO:
- Name: {customer_data.get('name')}
- Company: {customer_data.get('company')}
- Relationship: {interaction_history.get('summary', 'New contact')}

SENTIMENT ANALYSIS:
- Type: {sentiment_analysis.get('sentiment', {}).get('type')}
- Emotion: {sentiment_analysis.get('sentiment', {}).get('emotion')}
- Urgency: {sentiment_analysis.get('urgency')}
- Concerns: {', '.join(sentiment_analysis.get('concerns', []))}

RECOMMENDED APPROACH:
{sentiment_analysis.get('response_approach')}

Generate a {tone} response that:
1. Addresses their concerns directly
2. Shows empathy and understanding
3. Provides solutions or next steps
4. Maintains appropriate tone
5. Ends with clear call-to-action

Response:
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=500)
            
            return {
                'success': True,
                'response': response.strip(),
                'tone_used': tone,
                'sentiment_analysis': sentiment_analysis
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                'success': False,
                'message': f"Failed to generate response: {str(e)}"
            }
    
    def _get_recipient_history(self, customer_id: Optional[int]) -> Dict[str, Any]:
        """Get interaction history for recipient"""
        if not customer_id:
            return {'summary': 'No previous interactions', 'count': 0}
        
        try:
            db = db_helper.get_db()
            cursor = db.cursor()
            
            # Get recent interactions
            cursor.execute("""
                SELECT type, notes, created_at 
                FROM interactions 
                WHERE customer_id = ? 
                ORDER BY created_at DESC 
                LIMIT 5
            """, (customer_id,))
            
            interactions = cursor.fetchall()
            
            if not interactions:
                return {'summary': 'No previous interactions', 'count': 0}
            
            summary = f"Previous interactions: {len(interactions)} total. "
            recent_types = [i[0] for i in interactions[:3]]
            summary += f"Recent: {', '.join(recent_types)}"
            
            return {
                'summary': summary,
                'count': len(interactions),
                'recent': [{'type': i[0], 'notes': i[1], 'date': i[2]} for i in interactions]
            }
            
        except Exception as e:
            print(f"Error getting history: {e}")
            return {'summary': 'Unable to retrieve history', 'count': 0}
    
    def _build_personalization_context(self, recipient_data: Dict, history: Dict) -> str:
        """Build personalization context string"""
        context_parts = []
        
        if history.get('count', 0) > 0:
            context_parts.append(f"Previous interactions: {history['summary']}")
        
        if recipient_data.get('company'):
            context_parts.append(f"Works at {recipient_data['company']}")
        
        if recipient_data.get('industry'):
            context_parts.append(f"Industry: {recipient_data['industry']}")
        
        if recipient_data.get('lead_score'):
            context_parts.append(f"Lead score: {recipient_data['lead_score']}/100")
        
        return '\n'.join(context_parts) if context_parts else 'First-time contact'
    
    def _analyze_lead_behavior(self, lead_data: Dict) -> str:
        """Analyze lead behavior patterns"""
        behaviors = []
        
        if lead_data.get('lead_score', 0) > 70:
            behaviors.append("High engagement level")
        
        if lead_data.get('source'):
            behaviors.append(f"Came from {lead_data['source']}")
        
        if lead_data.get('website'):
            behaviors.append("Has active website presence")
        
        return '\n'.join(behaviors) if behaviors else 'Limited behavioral data available'
    
    def _extract_section(self, text: str, marker: str) -> str:
        """Extract section from formatted text"""
        try:
            if marker not in text:
                return text.strip()
            
            parts = text.split(marker)
            if len(parts) < 2:
                return text.strip()
            
            # Get content after marker
            content = parts[1]
            
            # Stop at next marker or double newline
            for next_marker in ['SUBJECT:', 'BODY:', 'SIGNATURE:', 'SENTIMENT:', 'EMOTION:', 
                               'URGENCY:', 'CONCERNS:', 'RECOMMENDED_TONE:', 'RESPONSE_APPROACH:']:
                if next_marker in content and next_marker != marker:
                    content = content.split(next_marker)[0]
            
            return content.strip()
            
        except Exception:
            return text.strip()
    
    def _extract_template_variations(self, text: str, field: str) -> List[str]:
        """Extract template variations for A/B testing"""
        variations = []
        
        # Look for numbered variations or bullet points
        lines = text.split('\n')
        for line in lines:
            if field.lower() in line.lower() and ':' in line:
                variations.append(line.split(':')[-1].strip())
            elif re.match(r'^\d+\.', line.strip()) or line.strip().startswith('-'):
                cleaned = re.sub(r'^\d+\.|^-', '', line).strip()
                if cleaned and len(cleaned) > 10:
                    variations.append(cleaned)
        
        return variations[:3] if variations else [f"Default {field}"]
    
    def _clean_template(self, text: str) -> str:
        """Clean and format template text"""
        # Remove markdown formatting
        text = re.sub(r'\*\*|__', '', text)
        # Remove extra whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def _extract_tokens(self, template: str) -> List[str]:
        """Extract personalization tokens from template"""
        tokens = re.findall(r'\[([A-Z_]+)\]', template)
        return list(set(tokens))
