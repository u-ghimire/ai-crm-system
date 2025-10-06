# modules/lead_scoring.py
"""
Lead Scoring Module - Machine Learning based lead scoring
Uses multiple factors to calculate lead quality and conversion probability
"""

import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import numpy as np

class LeadScoring:
    def __init__(self):
        """Initialize lead scoring system"""
        # Scoring weights for different factors
        self.weights = {
            'budget': 0.25,
            'industry_fit': 0.15,
            'company_size': 0.15,
            'engagement': 0.20,
            'timeline': 0.10,
            'decision_maker': 0.15
        }
        
        # Industry scoring map (based on typical conversion rates)
        self.industry_scores = {
            'technology': 85,
            'finance': 80,
            'healthcare': 75,
            'manufacturing': 70,
            'retail': 65,
            'education': 60,
            'non-profit': 50,
            'other': 55
        }
        
        # Define high-value behaviors
        self.engagement_activities = {
            'email_open': 5,
            'email_click': 10,
            'website_visit': 8,
            'demo_request': 25,
            'phone_call': 20,
            'meeting': 30,
            'proposal_view': 15,
            'chatbot': 7
        }
    
    def calculate_score(self, customer_data: Dict, interaction_history: List = None) -> float:
        """
        Calculate lead score based on multiple factors
        Returns a score between 0-100
        """
        scores = {}
        
        # Budget Score (0-100)
        scores['budget'] = self._calculate_budget_score(customer_data.get('budget', 0))
        
        # Industry Fit Score (0-100)
        scores['industry_fit'] = self._calculate_industry_score(customer_data.get('industry', 'other'))
        
        # Company Size Score (0-100)
        scores['company_size'] = self._calculate_company_size_score(
            customer_data.get('company', ''),
            customer_data.get('website', None)
        )
        
        # Engagement Score (0-100)
        scores['engagement'] = self._calculate_engagement_score(interaction_history or [])
        
        # Timeline Score (0-100)
        scores['timeline'] = self._calculate_timeline_score(customer_data)
        
        # Decision Maker Score (0-100)
        scores['decision_maker'] = self._calculate_decision_maker_score(customer_data)
        
        # Calculate weighted average
        total_score = 0
        for factor, weight in self.weights.items():
            total_score += scores.get(factor, 50) * weight
        
        # Apply behavioral modifiers
        total_score = self._apply_modifiers(total_score, customer_data, interaction_history)
        
        # Ensure score is between 0 and 100
        return max(0, min(100, round(total_score, 2)))
    
    def get_insights(self, customer_data: Dict) -> Dict:
        """Generate detailed insights about the lead"""
        score = self.calculate_score(customer_data)
        
        insights = {
            'score': score,
            'grade': self._get_grade(score),
            'priority': self._get_priority(score),
            'conversion_probability': self._estimate_conversion_probability(score),
            'strengths': [],
            'weaknesses': [],
            'recommendations': []
        }
        
        # Analyze strengths and weaknesses
        if customer_data.get('budget', 0) > 10000:
            insights['strengths'].append('High budget availability')
        else:
            insights['weaknesses'].append('Limited budget')
            insights['recommendations'].append('Focus on ROI demonstration')
        
        industry = customer_data.get('industry', 'other')
        if industry in ['technology', 'finance', 'healthcare']:
            insights['strengths'].append(f'High-converting industry: {industry}')
        
        if score > 70:
            insights['recommendations'].append('Schedule immediate follow-up')
            insights['recommendations'].append('Assign to senior sales rep')
        elif score > 40:
            insights['recommendations'].append('Nurture with targeted content')
            insights['recommendations'].append('Schedule follow-up in 1 week')
        else:
            insights['recommendations'].append('Add to long-term nurture campaign')
            insights['recommendations'].append('Re-evaluate in 30 days')
        
        return insights
    
    def _calculate_budget_score(self, budget: float) -> float:
        """Calculate score based on budget"""
        try:
            budget = float(budget)
        except (TypeError, ValueError):
            budget = 0
        if budget >= 100000:
            return 100
        elif budget >= 50000:
            return 85
        elif budget >= 25000:
            return 70
        elif budget >= 10000:
            return 55
        elif budget >= 5000:
            return 40
        elif budget > 0:
            return 25
        else:
            return 10  # Unknown budget
    
    def _calculate_industry_score(self, industry: str) -> float:
        """Calculate score based on industry"""
        return self.industry_scores.get(industry.lower(), 55)
    
    def _calculate_company_size_score(self, company: str, website: str = None) -> float:
        """Estimate company size score using OpenAI API, fallback to heuristic if needed"""
        import openai
        if not company:
            return 30
        
        # Try AI-powered estimation first
        prompt = f"""
Estimate the company size category for the following company. Respond with one of: 'Large Enterprise', 'Medium Business', 'Small Business', or 'Startup'.
Company Name: {company}
"""
        if website:
            prompt += f"\nWebsite: {website}"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a business analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            answer = response.choices[0].message['content'].strip().lower()
            if 'large' in answer:
                return 90
            elif 'medium' in answer:
                return 70
            elif 'small' in answer:
                return 50
            elif 'startup' in answer:
                return 40
        except Exception:
            pass  # Fall back to heuristic
        
        # Fallback to heuristic
        company_lower = company.lower()
        if any(word in company_lower for word in ['enterprise', 'global', 'international', 'corporation']):
            return 90
        elif any(word in company_lower for word in ['inc', 'llc', 'ltd', 'company']):
            return 70
        elif any(word in company_lower for word in ['startup', 'ventures']):
            return 50
        else:
            return 40
    
    def _calculate_engagement_score(self, interactions: List[Dict]) -> float:
        """Calculate engagement score based on interaction history"""
        if not interactions:
            return 20  # Base score for new leads
        
        total_engagement = 0
        recent_interactions = 0
        
        for interaction in interactions:
            # Get interaction type and calculate points
            interaction_type = interaction.get('type', '').lower()
            points = self.engagement_activities.get(interaction_type, 3)
            
            # Recent interactions are worth more
            if self._is_recent_interaction(interaction, days=7):
                points *= 1.5
                recent_interactions += 1
            elif self._is_recent_interaction(interaction, days=30):
                points *= 1.2
            
            total_engagement += points
        
        # Calculate score (cap at 100)
        engagement_score = min(100, total_engagement)
        
        # Bonus for consistent recent engagement
        if recent_interactions >= 3:
            engagement_score = min(100, engagement_score + 15)
        
        return engagement_score
    
    def _calculate_timeline_score(self, customer_data: Dict) -> float:
        """Calculate score based on buying timeline"""
        status = customer_data.get('status', 'lead')
        
        status_scores = {
            'hot': 95,
            'qualified': 80,
            'interested': 65,
            'lead': 50,
            'cold': 20,
            'customer': 100
        }
        
        return status_scores.get(status.lower(), 50)
    
    def _calculate_decision_maker_score(self, customer_data: Dict) -> float:
        """Calculate score based on contact's decision-making authority"""
        notes = str(customer_data.get('notes', '')).lower()
        name = str(customer_data.get('name', '')).lower()
        
        # Check for decision-maker indicators
        decision_indicators = ['ceo', 'cto', 'cfo', 'president', 'director', 'manager', 'head of', 'vp', 'vice president', 'owner']
        
        for indicator in decision_indicators:
            if indicator in notes or indicator in name:
                if indicator in ['ceo', 'cto', 'cfo', 'president', 'owner']:
                    return 95
                elif indicator in ['vp', 'vice president', 'director']:
                    return 80
                else:
                    return 65
        
        return 40  # Unknown authority level
    
    def _apply_modifiers(self, base_score: float, customer_data: Dict, interactions: List) -> float:
        """Apply behavioral modifiers to the base score"""
        modified_score = base_score
        
        # Negative modifiers
        if interactions:
            # Check for negative signals
            negative_interactions = [i for i in interactions if 
                                    any(word in str(i.get('notes', '')).lower() 
                                        for word in ['not interested', 'too expensive', 'no budget', 'maybe later'])]
            
            if negative_interactions:
                modified_score *= 0.7  # Reduce score by 30%
        
        # Positive modifiers
        if customer_data.get('website'):
            modified_score += 5  # Has website info
        
        if customer_data.get('phone') and customer_data.get('email'):
            modified_score += 5  # Complete contact info
        
        # Recency modifier
        if interactions and len(interactions) > 0:
            last_interaction = max(interactions, key=lambda x: x.get('created_at', ''))
            if self._is_recent_interaction(last_interaction, days=3):
                modified_score += 10  # Very recent interaction
        
        return modified_score
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 85:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 55:
            return 'C'
        elif score >= 40:
            return 'D'
        else:
            return 'F'
    
    def _get_priority(self, score: float) -> str:
        """Determine lead priority"""
        if score >= 70:
            return 'High'
        elif score >= 40:
            return 'Medium'
        else:
            return 'Low'
    
    def _estimate_conversion_probability(self, score: float) -> float:
        """Estimate probability of conversion based on score"""
        # Sigmoid function for smooth probability mapping
        x = (score - 50) / 10  # Center at 50, scale by 10
        probability = 1 / (1 + np.exp(-x))
        return round(probability * 100, 1)
    
    def _is_recent_interaction(self, interaction: Dict, days: int = 30) -> bool:
        """Check if interaction is within specified days"""
        if not interaction or not interaction.get('created_at'):
            return False
        
        try:
            # Parse the date string
            created_str = str(interaction['created_at'])
            # Handle different date formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
                try:
                    created = datetime.strptime(created_str.split('.')[0], fmt)
                    days_diff = (datetime.now() - created).days
                    return days_diff <= days
                except:
                    continue
        except:
            pass
        
        return False
    
    def batch_score_leads(self, customers: List[Dict]) -> List[Dict]:
        """Score multiple leads at once"""
        scored_leads = []
        
        for customer in customers:
            score = self.calculate_score(customer)
            customer_copy = customer.copy()
            customer_copy['lead_score'] = score
            customer_copy['lead_grade'] = self._get_grade(score)
            customer_copy['priority'] = self._get_priority(score)
            scored_leads.append(customer_copy)
        
        # Sort by score descending
        scored_leads.sort(key=lambda x: x['lead_score'], reverse=True)
        
        return scored_leads