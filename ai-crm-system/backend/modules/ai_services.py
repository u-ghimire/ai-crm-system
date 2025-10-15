# modules/ai_services.py
"""
AI Services Module - Integrates with a local AI model for intelligent insights
Handles all AI-powered features including text generation and analysis
"""

import json
from typing import Dict, List, Any
from datetime import datetime
from .huggingface_ai import HuggingFaceAI

class AIServices:
    def __init__(self, ai_model: HuggingFaceAI):
        """Initialize AI services with a loaded AI model"""
        self.ai_model = ai_model
    
    def generate_completion(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate AI completion for given prompt"""
        # The 'max_tokens' parameter is now 'max_length' in the new implementation
        return self.ai_model.generate(prompt, max_length=max_tokens)
    
    def generate_customer_insights(self, customer_data: Dict) -> Dict:
        """Generate AI insights for a specific customer"""
        prompt = f"""
        Analyze the following customer data and provide actionable insights:
        
        Customer: {customer_data.get('name', 'Unknown')}
        Company: {customer_data.get('company', 'N/A')}
        Industry: {customer_data.get('industry', 'N/A')}
        Status: {customer_data.get('status', 'lead')}
        Lead Score: {customer_data.get('lead_score', 0)}
        Budget: ${customer_data.get('budget', 0)}
        Location: {customer_data.get('location', 'N/A')}
        
        Provide:
        1. Customer potential assessment
        2. Recommended next actions
        3. Potential challenges
        4. Opportunity size estimation
        5. Best engagement strategy
        """
        
        insights_text = self.generate_completion(prompt)
        
        # Parse the response into structured format
        insights = {
            'summary': insights_text,
            'potential': self._extract_potential(insights_text),
            'next_actions': self._extract_actions(insights_text),
            'engagement_tips': self._extract_engagement_tips(insights_text),
            'generated_at': datetime.now().isoformat()
        }
        
        return insights
    
    def generate_business_insights(self, business_data: Dict) -> Dict:
        """Generate overall business insights"""
        customers = business_data.get('customers', [])
        interactions = business_data.get('interactions', [])
        revenue = business_data.get('revenue', 0)
        
        prompt = f"""
        Analyze the following business metrics and provide strategic insights:
        
        Total Customers: {len(customers)}
        Recent Interactions: {len(interactions)}
        Monthly Revenue: ${revenue}
        
        Top Industries: {self._get_top_industries(customers)}
        Average Lead Score: {self._get_average_lead_score(customers)}
        
        Provide:
        1. Business health assessment
        2. Growth opportunities
        3. Risk areas to monitor
        4. Recommended focus areas
        5. Market trends to consider
        """
        
        insights_text = self.generate_completion(prompt)
        
        return {
            'summary': insights_text,
            'metrics_analysis': self._analyze_metrics(business_data),
            'recommendations': self._extract_recommendations(insights_text),
            'generated_at': datetime.now().isoformat()
        }
    
    def generate_email_template(self, customer_data: Dict, purpose: str = 'follow-up') -> str:
        """Generate personalized email template"""
        prompt = f"""
        Create a professional email template for the following purpose: {purpose}
        
        Customer Details:
        Name: {customer_data.get('name', 'Valued Customer')}
        Company: {customer_data.get('company', '')}
        Industry: {customer_data.get('industry', '')}
        
        Email should be:
        - Professional and personalized
        - Clear call-to-action
        - Appropriate for {purpose}
        - Between 100-150 words
        """
        
        return self.generate_completion(prompt, max_tokens=300)
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of customer communication"""
        prompt = f"""
        Analyze the sentiment of the following text and provide:
        1. Overall sentiment (positive/neutral/negative)
        2. Confidence score (0-100)
        3. Key emotions detected
        4. Recommended response tone
        
        Text: {text}
        """
        
        response = self.generate_completion(prompt, temperature=0.3)
        
        return {
            'analysis': response,
            'sentiment': self._extract_sentiment(response),
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_sales_pitch(self, customer_data: Dict, product_info: str = "") -> str:
        """Generate customized sales pitch"""
        prompt = f"""
        Create a compelling sales pitch for:
        
        Customer: {customer_data.get('name')}
        Company: {customer_data.get('company')}
        Industry: {customer_data.get('industry')}
        Budget: ${customer_data.get('budget', 'Not specified')}
        
        Product/Service: {product_info if product_info else 'CRM Solution'}
        
        The pitch should:
        - Address industry-specific pain points
        - Highlight relevant benefits
        - Include a value proposition
        - Be concise and impactful
        """
        
        return self.generate_completion(prompt, max_tokens=400)
    
    def predict_churn_risk(self, customer_data: Dict, interaction_history: List) -> Dict:
        """Predict customer churn risk"""
        recent_interactions = len([i for i in interaction_history if self._is_recent(i)])
        
        prompt = f"""
        Assess churn risk for the following customer:
        
        Customer Status: {customer_data.get('status')}
        Lead Score: {customer_data.get('lead_score')}
        Last Interaction: {self._get_last_interaction_date(interaction_history)}
        Recent Interactions (30 days): {recent_interactions}
        
        Provide:
        1. Churn risk level (low/medium/high)
        2. Risk factors identified
        3. Retention strategies
        4. Urgency of action required
        """
        
        response = self.generate_completion(prompt)
        
        return {
            'risk_assessment': response,
            'risk_level': self._extract_risk_level(response),
            'retention_strategies': self._extract_strategies(response),
            'analyzed_at': datetime.now().isoformat()
        }
    
    # Helper methods
    def _get_fallback_response(self, prompt: str) -> str:
        """Provide fallback response when API is unavailable"""
        if "insight" in prompt.lower():
            return "Based on the available data, this customer shows moderate potential. Consider scheduling a follow-up call to discuss their specific needs and budget constraints."
        elif "email" in prompt.lower():
            return "Subject: Following up on our conversation\n\nDear Customer,\n\nI hope this email finds you well. I wanted to follow up on our recent discussion and see if you have any questions about our solutions. Please let me know if you'd like to schedule a call to discuss further.\n\nBest regards"
        else:
            return "Analysis in progress. Please ensure AI API key is configured for detailed insights."
    
    def _extract_potential(self, text: str) -> str:
        """Extract potential assessment from AI response"""
        lines = text.split('\n')
        for line in lines:
            if 'potential' in line.lower():
                return line.strip()
        return "Moderate potential identified"
    
    def _extract_actions(self, text: str) -> List[str]:
        """Extract recommended actions from AI response"""
        actions = []
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['recommend', 'should', 'action', 'next']):
                actions.append(line.strip())
        return actions[:3] if actions else ["Schedule follow-up", "Send product information", "Assess needs"]
    
    def _extract_engagement_tips(self, text: str) -> List[str]:
        """Extract engagement tips from AI response"""
        tips = []
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['engagement', 'strategy', 'approach', 'communicate']):
                tips.append(line.strip())
        return tips[:3] if tips else ["Personalize communication", "Focus on value proposition", "Be responsive"]
    
    def _get_top_industries(self, customers: List[Dict]) -> str:
        """Get top industries from customer list"""
        industries = {}
        for customer in customers:
            industry = customer.get('industry', 'Unknown')
            industries[industry] = industries.get(industry, 0) + 1
        
        sorted_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)
        return ', '.join([f"{ind[0]} ({ind[1]})" for ind in sorted_industries[:3]])
    
    def _get_average_lead_score(self, customers: List[Dict]) -> float:
        """Calculate average lead score"""
        if not customers:
            return 0
        
        scores = [c.get('lead_score', 0) for c in customers]
        return round(sum(scores) / len(scores), 2)
    
    def _analyze_metrics(self, business_data: Dict) -> Dict:
        """Analyze business metrics"""
        customers = business_data.get('customers', [])
        
        return {
            'total_customers': len(customers),
            'high_value_leads': len([c for c in customers if c.get('lead_score', 0) > 70]),
            'conversion_potential': self._calculate_conversion_potential(customers),
            'market_coverage': self._get_top_industries(customers)
        }
    
    def _calculate_conversion_potential(self, customers: List[Dict]) -> str:
        """Calculate conversion potential"""
        high_score_count = len([c for c in customers if c.get('lead_score', 0) > 70])
        if not customers:
            return "Low"
        
        ratio = high_score_count / len(customers)
        if ratio > 0.3:
            return "High"
        elif ratio > 0.15:
            return "Moderate"
        else:
            return "Low"
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(word in line.lower() for word in ['recommend', 'focus', 'consider', 'should']):
                recommendations.append(line.strip())
        return recommendations[:5] if recommendations else ["Focus on high-value leads", "Improve follow-up processes", "Expand market reach"]
    
    def _extract_sentiment(self, text: str) -> str:
        """Extract sentiment from analysis"""
        text_lower = text.lower()
        if 'positive' in text_lower:
            return 'positive'
        elif 'negative' in text_lower:
            return 'negative'
        else:
            return 'neutral'
    
    def _extract_risk_level(self, text: str) -> str:
        """Extract risk level from analysis"""
        text_lower = text.lower()
        if 'high' in text_lower and 'risk' in text_lower:
            return 'high'
        elif 'medium' in text_lower or 'moderate' in text_lower:
            return 'medium'
        else:
            return 'low'
    
    def _extract_strategies(self, text: str) -> List[str]:
        """Extract retention strategies"""
        strategies = []
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['strategy', 'retain', 'engage', 'offer']):
                strategies.append(line.strip())
        return strategies[:3] if strategies else ["Increase engagement", "Offer personalized solutions", "Schedule regular check-ins"]
    
    def _is_recent(self, interaction: Dict, days: int = 30) -> bool:
        """Check if interaction is recent"""
        if not interaction.get('created_at'):
            return False
        
        try:
            created = datetime.fromisoformat(str(interaction['created_at']))
            days_diff = (datetime.now() - created).days
            return days_diff <= days
        except:
            return False
    
    def _get_last_interaction_date(self, interactions: List[Dict]) -> str:
        """Get last interaction date"""
        if not interactions:
            return "No interactions"
        
        try:
            sorted_interactions = sorted(interactions, key=lambda x: x.get('created_at', ''), reverse=True)
            if sorted_interactions:
                return sorted_interactions[0].get('created_at', 'Unknown')
        except:
            pass
        
        return "Unknown"