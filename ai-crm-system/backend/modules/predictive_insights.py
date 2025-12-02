"""
Predictive Insights Module - AI-powered predictions and forecasting
Includes deal success probability, churn prediction, and revenue forecasting
"""

import json
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .groq_ai import GroqAI
from .db_helper import get_db

class PredictiveInsights:
    def __init__(self, ai_model: GroqAI):
        """Initialize predictive insights engine"""
        self.ai_model = ai_model
        
        # Deal stage conversion rates (historical averages)
        self.stage_conversion_rates = {
            'Lead': 0.15,
            'Qualified': 0.35,
            'Proposal': 0.50,
            'Negotiation': 0.70,
            'Closed Won': 1.0,
            'Closed Lost': 0.0
        }
        
        # Churn risk factors
        self.churn_risk_factors = {
            'no_interaction_30_days': 30,
            'no_interaction_60_days': 50,
            'no_interaction_90_days': 70,
            'negative_sentiment': 25,
            'low_engagement': 20,
            'support_tickets': 15
        }
    
    def predict_deal_success(self, deal_id: int, deal_data: Dict = None) -> Dict:
        """
        Predict probability of deal success using multiple factors
        
        Returns:
            Dict with probability, confidence, factors, and recommendations
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get deal data if not provided
            if not deal_data:
                cursor.execute('''
                    SELECT o.*, c.name as customer_name, c.company, c.industry, 
                           c.lead_score, c.budget
                    FROM opportunities o
                    LEFT JOIN customers c ON o.customer_id = c.id
                    WHERE o.id = ?
                ''', (deal_id,))
                deal_data = dict(cursor.fetchone() or {})
            
            if not deal_data:
                return {'error': 'Deal not found'}
            
            # Calculate base probability from current stage
            stage = deal_data.get('stage', 'Lead')
            base_probability = self.stage_conversion_rates.get(stage, 0.3)
            
            # Gather factors that influence probability
            factors = self._analyze_deal_factors(deal_data, cursor)
            
            # Calculate adjusted probability
            adjusted_probability = self._calculate_adjusted_probability(base_probability, factors)
            
            # Get AI insights
            ai_insights = self._get_ai_deal_insights(deal_data, factors)
            
            # Calculate confidence based on data completeness
            confidence = self._calculate_confidence(deal_data, factors)
            
            # Generate recommendations
            recommendations = self._generate_deal_recommendations(deal_data, factors, adjusted_probability)
            
            return {
                'deal_id': deal_id,
                'deal_title': deal_data.get('title', 'Unknown'),
                'current_stage': stage,
                'win_probability': round(adjusted_probability * 100, 1),
                'confidence_score': round(confidence, 1),
                'base_probability': round(base_probability * 100, 1),
                'factors': factors,
                'ai_insights': ai_insights,
                'recommendations': recommendations,
                'risk_level': self._assess_risk_level(adjusted_probability, factors),
                'predicted_close_date': self._predict_close_date(deal_data, factors),
                'estimated_value': deal_data.get('value', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Deal prediction error: {e}")
            return {'error': str(e)}
    
    def _analyze_deal_factors(self, deal_data: Dict, cursor) -> Dict:
        """Analyze factors that influence deal success"""
        factors = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        # Factor 1: Deal value
        value = deal_data.get('value', 0)
        if value > 100000:
            factors['positive'].append({'factor': 'High deal value', 'impact': 15, 'value': f'${value:,.0f}'})
        elif value < 5000:
            factors['negative'].append({'factor': 'Low deal value', 'impact': -10, 'value': f'${value:,.0f}'})
        
        # Factor 2: Company size/budget
        budget = deal_data.get('budget', 0)
        if budget and budget > 100000:
            factors['positive'].append({'factor': 'Large budget', 'impact': 12, 'value': f'${budget:,.0f} budget'})
        
        # Factor 3: Lead score
        lead_score = deal_data.get('lead_score', 0)
        if lead_score > 70:
            factors['positive'].append({'factor': 'High lead score', 'impact': 20, 'value': f'{lead_score}/100'})
        elif lead_score < 40:
            factors['negative'].append({'factor': 'Low lead score', 'impact': -15, 'value': f'{lead_score}/100'})
        
        # Factor 4: Time in current stage
        days_in_stage = deal_data.get('days_in_stage', 0)
        stage = deal_data.get('stage', 'Lead')
        expected_days = {'Lead': 14, 'Qualified': 21, 'Proposal': 14, 'Negotiation': 10}.get(stage, 30)
        
        if days_in_stage > expected_days * 2:
            factors['negative'].append({'factor': 'Stalled in stage', 'impact': -20, 'value': f'{days_in_stage} days'})
        elif days_in_stage < expected_days / 2:
            factors['positive'].append({'factor': 'Fast progression', 'impact': 10, 'value': f'{days_in_stage} days'})
        
        # Factor 5: Contact seniority
        contact_title = (deal_data.get('contact_title', '') or '').lower()
        if any(word in contact_title for word in ['ceo', 'president', 'vp', 'director', 'cto', 'cfo']):
            factors['positive'].append({'factor': 'Senior decision maker', 'impact': 18, 'value': contact_title})
        
        # Factor 6: Industry fit
        industry = (deal_data.get('industry', '') or '').lower()
        high_converting_industries = ['technology', 'finance', 'healthcare']
        if any(ind in industry for ind in high_converting_industries):
            factors['positive'].append({'factor': 'High-converting industry', 'impact': 12, 'value': industry})
        
        # Factor 7: Recent activity
        cursor.execute('''
            SELECT COUNT(*) FROM activities 
            WHERE deal_id = ? AND created_at >= datetime('now', '-7 days')
        ''', (deal_data.get('id'),))
        recent_activity_count = cursor.fetchone()[0]
        
        if recent_activity_count >= 3:
            factors['positive'].append({'factor': 'High recent engagement', 'impact': 15, 'value': f'{recent_activity_count} activities'})
        elif recent_activity_count == 0:
            factors['negative'].append({'factor': 'No recent activity', 'impact': -25, 'value': 'Last 7 days'})
        
        # Factor 8: Expected close date proximity
        expected_close = deal_data.get('expected_close_date')
        if expected_close:
            try:
                close_date = datetime.fromisoformat(str(expected_close))
                days_until_close = (close_date - datetime.now()).days
                
                if 0 < days_until_close < 7:
                    factors['positive'].append({'factor': 'Closing soon', 'impact': 10, 'value': f'{days_until_close} days'})
                elif days_until_close < 0:
                    factors['negative'].append({'factor': 'Past expected close date', 'impact': -20, 'value': 'Overdue'})
            except:
                pass
        
        return factors
    
    def _calculate_adjusted_probability(self, base_probability: float, factors: Dict) -> float:
        """Calculate adjusted probability based on factors"""
        adjustment = 0
        
        # Sum up positive impacts
        for factor in factors['positive']:
            adjustment += factor['impact']
        
        # Sum up negative impacts
        for factor in factors['negative']:
            adjustment += factor['impact']  # Already negative
        
        # Convert impact to probability adjustment (0-100 scale)
        probability_adjustment = adjustment / 100.0
        
        # Apply adjustment
        adjusted = base_probability + probability_adjustment
        
        # Ensure probability stays between 0 and 1
        return max(0.0, min(1.0, adjusted))
    
    def _get_ai_deal_insights(self, deal_data: Dict, factors: Dict) -> str:
        """Get AI-generated insights about the deal"""
        positive_factors = [f['factor'] for f in factors['positive']]
        negative_factors = [f['factor'] for f in factors['negative']]
        
        prompt = f"""Analyze this sales deal and provide strategic insights:

Deal: {deal_data.get('title', 'Unknown')}
Stage: {deal_data.get('stage', 'Unknown')}
Value: ${deal_data.get('value', 0):,.0f}
Company: {deal_data.get('industry', 'Unknown')} industry

Positive factors: {', '.join(positive_factors) if positive_factors else 'None'}
Negative factors: {', '.join(negative_factors) if negative_factors else 'None'}

Provide (in 2-3 sentences):
1. Overall assessment
2. Key action to improve win probability
3. Main risk to address"""

        try:
            insights = self.ai_model.generate(prompt, max_length=250)
            return insights.strip()
        except Exception as e:
            print(f"AI insights error: {e}")
            return "Deal shows moderate potential. Focus on maintaining engagement and addressing any objections promptly."
    
    def _calculate_confidence(self, deal_data: Dict, factors: Dict) -> float:
        """Calculate confidence score based on data completeness"""
        confidence = 50.0  # Base confidence
        
        # Check data completeness
        required_fields = ['value', 'stage', 'expected_close_date', 'company_id', 'primary_contact_id']
        complete_fields = sum(1 for field in required_fields if deal_data.get(field))
        completeness_score = (complete_fields / len(required_fields)) * 30
        confidence += completeness_score
        
        # More factors = higher confidence
        total_factors = len(factors['positive']) + len(factors['negative'])
        factor_score = min(20, total_factors * 3)
        confidence += factor_score
        
        return min(100.0, confidence)
    
    def _generate_deal_recommendations(self, deal_data: Dict, factors: Dict, probability: float) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if probability < 0.3:
            recommendations.append("🚨 Low win probability - Consider re-qualifying this opportunity")
            recommendations.append("Schedule discovery call to understand blockers")
        elif probability < 0.5:
            recommendations.append("⚠️ Moderate risk - Increase engagement frequency")
            recommendations.append("Provide case studies or success stories")
        else:
            recommendations.append("✅ High win probability - Maintain momentum")
            recommendations.append("Prepare contract and next steps")
        
        # Address specific negative factors
        for factor in factors['negative']:
            if 'stalled' in factor['factor'].lower():
                recommendations.append("Move deal forward with specific next action")
            elif 'no recent activity' in factor['factor'].lower():
                recommendations.append("Schedule immediate follow-up call or meeting")
            elif 'overdue' in factor['value'].lower():
                recommendations.append("Reassess timeline and reset expectations")
        
        # Leverage positive factors
        if any('senior decision maker' in f['factor'].lower() for f in factors['positive']):
            recommendations.append("Leverage decision maker relationship for faster close")
        
        return recommendations[:5]  # Return top 5
    
    def _assess_risk_level(self, probability: float, factors: Dict) -> str:
        """Assess overall risk level"""
        negative_count = len(factors['negative'])
        
        if probability < 0.3 or negative_count >= 3:
            return 'High Risk'
        elif probability < 0.6 or negative_count >= 2:
            return 'Medium Risk'
        else:
            return 'Low Risk'
    
    def _predict_close_date(self, deal_data: Dict, factors: Dict) -> Optional[str]:
        """Predict realistic close date"""
        stage = deal_data.get('stage', 'Lead')
        expected_close = deal_data.get('expected_close_date')
        
        # Estimate days to close based on stage
        days_by_stage = {
            'Lead': 60,
            'Qualified': 45,
            'Proposal': 30,
            'Negotiation': 14,
            'Closed Won': 0,
            'Closed Lost': 0
        }
        
        estimated_days = days_by_stage.get(stage, 30)
        
        # Adjust based on factors
        if any('stalled' in f['factor'].lower() for f in factors['negative']):
            estimated_days *= 1.5  # 50% longer if stalled
        elif any('fast progression' in f['factor'].lower() for f in factors['positive']):
            estimated_days *= 0.7  # 30% faster if moving quickly
        
        predicted_date = datetime.now() + timedelta(days=int(estimated_days))
        return predicted_date.strftime('%Y-%m-%d')
    
    def predict_churn_risk(self, customer_id: int = None, contact_id: int = None) -> Dict:
        """
        Predict customer churn risk
        
        Args:
            customer_id: Legacy customer ID (for backwards compatibility)
            contact_id: Contact ID (new system)
        
        Returns:
            Dict with risk score, level, factors, and retention strategies
        """
        try:
            db = get_db()
            cursor = db.cursor()
            
            # Get contact/customer data
            entity_id = contact_id or customer_id
            if not entity_id:
                return {'error': 'contact_id or customer_id required'}
            
            cursor.execute('''
                SELECT * FROM customers WHERE id = ?
            ''', (entity_id,))
            
            data = dict(cursor.fetchone() or {})
            
            if not data:
                return {'error': 'Customer/Contact not found'}
            
            # Analyze churn factors
            risk_factors = self._analyze_churn_factors(data, cursor, entity_id)
            
            # Calculate risk score (0-100)
            risk_score = self._calculate_churn_score(risk_factors)
            
            # Determine risk level
            risk_level = self._get_churn_risk_level(risk_score)
            
            # Get AI insights
            ai_insights = self._get_ai_churn_insights(data, risk_factors, risk_score)
            
            # Generate retention strategies
            strategies = self._generate_retention_strategies(risk_factors, risk_level)
            
            return {
                'contact_id': contact_id or customer_id,
                'contact_name': data.get('name', 'Unknown'),
                'company': data.get('company', 'Unknown'),
                'churn_risk_score': round(risk_score, 1),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'ai_insights': ai_insights,
                'retention_strategies': strategies,
                'urgency': 'Immediate' if risk_score > 70 else 'High' if risk_score > 50 else 'Monitor',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Churn prediction error: {e}")
            return {'error': str(e)}
    
    def _analyze_churn_factors(self, data: Dict, cursor, entity_id: int) -> Dict:
        """Analyze factors contributing to churn risk"""
        factors = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': []
        }
        
        # Factor 1: Last interaction date
        cursor.execute('''
            SELECT MAX(created_at) FROM interactions 
            WHERE customer_id = ?
        ''', (entity_id,))
        last_interaction = cursor.fetchone()[0]
        
        if last_interaction:
            try:
                last_date = datetime.fromisoformat(str(last_interaction))
                days_since = (datetime.now() - last_date).days
                
                if days_since > 90:
                    factors['high_risk'].append({'factor': 'No contact in 90+ days', 'value': f'{days_since} days', 'impact': 30})
                elif days_since > 60:
                    factors['medium_risk'].append({'factor': 'No contact in 60+ days', 'value': f'{days_since} days', 'impact': 20})
                elif days_since > 30:
                    factors['medium_risk'].append({'factor': 'No contact in 30+ days', 'value': f'{days_since} days', 'impact': 10})
                else:
                    factors['low_risk'].append({'factor': 'Recent engagement', 'value': f'{days_since} days', 'impact': -15})
            except:
                factors['high_risk'].append({'factor': 'No interaction history', 'value': 'Unknown', 'impact': 25})
        else:
            factors['high_risk'].append({'factor': 'No interactions logged', 'value': '0 activities', 'impact': 35})
        
        # Factor 2: Deal history
        cursor.execute('''
            SELECT COUNT(*), SUM(CASE WHEN stage = 'Closed Won' THEN 1 ELSE 0 END)
            FROM deals WHERE primary_contact_id = ?
        ''', (entity_id,))
        deal_result = cursor.fetchone()
        total_deals = deal_result[0] or 0
        won_deals = deal_result[1] or 0
        
        if total_deals > 0 and won_deals == 0:
            factors['medium_risk'].append({'factor': 'No won deals', 'value': f'{total_deals} attempted', 'impact': 15})
        elif won_deals > 2:
            factors['low_risk'].append({'factor': 'Multiple successful deals', 'value': f'{won_deals} won', 'impact': -20})
        
        # Factor 3: Lead score (if available)
        lead_score = data.get('lead_score', 0)
        if lead_score < 30:
            factors['high_risk'].append({'factor': 'Low engagement score', 'value': f'{lead_score}/100', 'impact': 20})
        elif lead_score > 70:
            factors['low_risk'].append({'factor': 'High engagement score', 'value': f'{lead_score}/100', 'impact': -15})
        
        # Factor 4: Customer status
        status = data.get('status', 'lead')
        if status in ['cold', 'inactive', 'lost']:
            factors['high_risk'].append({'factor': 'Inactive status', 'value': status, 'impact': 25})
        elif status in ['customer', 'hot', 'active']:
            factors['low_risk'].append({'factor': 'Active customer', 'value': status, 'impact': -20})
        
        # Factor 5: Activity frequency trend
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN created_at >= datetime('now', '-30 days') THEN 1 END) as recent,
                COUNT(CASE WHEN created_at >= datetime('now', '-60 days') AND created_at < datetime('now', '-30 days') THEN 1 END) as previous
            FROM interactions
            WHERE customer_id = ?
        ''', (entity_id,))
        trend = cursor.fetchone()
        recent_count = trend[0] or 0
        previous_count = trend[1] or 0
        
        if previous_count > 0 and recent_count < previous_count * 0.5:
            factors['high_risk'].append({'factor': 'Declining engagement', 'value': f'{recent_count} vs {previous_count} activities', 'impact': 22})
        elif recent_count > previous_count:
            factors['low_risk'].append({'factor': 'Increasing engagement', 'value': f'{recent_count} vs {previous_count}', 'impact': -12})
        
        return factors
    
    def _calculate_churn_score(self, risk_factors: Dict) -> float:
        """Calculate overall churn risk score (0-100)"""
        base_score = 30.0  # Everyone has some baseline risk
        
        # Add risk from high-risk factors
        for factor in risk_factors['high_risk']:
            base_score += factor['impact']
        
        # Add risk from medium-risk factors
        for factor in risk_factors['medium_risk']:
            base_score += factor['impact']
        
        # Reduce risk based on low-risk factors
        for factor in risk_factors['low_risk']:
            base_score += factor['impact']  # Already negative
        
        return max(0.0, min(100.0, base_score))
    
    def _get_churn_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score >= 70:
            return 'Critical'
        elif risk_score >= 50:
            return 'High'
        elif risk_score >= 30:
            return 'Medium'
        else:
            return 'Low'
    
    def _get_ai_churn_insights(self, data: Dict, risk_factors: Dict, risk_score: float) -> str:
        """Get AI insights about churn risk"""
        high_risks = [f['factor'] for f in risk_factors['high_risk']]
        
        prompt = f"""Analyze customer churn risk:

Customer: {data.get('name', 'Unknown')} - {data.get('company', 'Unknown')}
Risk Score: {risk_score}/100
High Risk Factors: {', '.join(high_risks) if high_risks else 'None'}

Provide brief assessment (2 sentences):
1. Why are they at risk?
2. What's the best retention approach?"""

        try:
            return self.ai_model.generate(prompt, max_length=150).strip()
        except:
            return f"Customer shows {self._get_churn_risk_level(risk_score).lower()} churn risk. Immediate re-engagement recommended."
    
    def _generate_retention_strategies(self, risk_factors: Dict, risk_level: str) -> List[str]:
        """Generate personalized retention strategies"""
        strategies = []
        
        if risk_level in ['Critical', 'High']:
            strategies.append("🚨 Schedule immediate check-in call with account owner")
            strategies.append("Offer exclusive benefit or discount to re-engage")
            strategies.append("Identify pain points and address concerns proactively")
        else:
            strategies.append("✅ Maintain regular touch points (monthly minimum)")
            strategies.append("Share relevant content and industry insights")
        
        # Address specific risk factors
        high_risk_factors = risk_factors['high_risk']
        
        if any('no contact' in f['factor'].lower() for f in high_risk_factors):
            strategies.append("Create structured follow-up campaign")
            strategies.append("Send personalized value-add communication")
        
        if any('declining engagement' in f['factor'].lower() for f in high_risk_factors):
            strategies.append("Conduct satisfaction survey")
            strategies.append("Introduce new features or services")
        
        if any('no won deals' in f['factor'].lower() for f in risk_factors['medium_risk']):
            strategies.append("Understand barriers to purchase")
            strategies.append("Offer pilot program or trial period")
        
        return strategies[:6]  # Return top 6
    
    def batch_predict_deal_success(self, deal_ids: List[int] = None) -> List[Dict]:
        """Predict success for multiple deals"""
        db = get_db()
        cursor = db.cursor()
        
        if not deal_ids:
            # Get all active deals
            cursor.execute("SELECT id FROM opportunities WHERE status = 'open' OR stage NOT IN ('won', 'lost')")
            deal_ids = [row[0] for row in cursor.fetchall()]
        
        predictions = []
        for deal_id in deal_ids[:50]:  # Limit to 50 for performance
            prediction = self.predict_deal_success(deal_id)
            if 'error' not in prediction:
                predictions.append(prediction)
        
        # Sort by win probability descending
        predictions.sort(key=lambda x: x['win_probability'], reverse=True)
        
        return predictions
    
    def batch_predict_churn(self, contact_ids: List[int] = None) -> List[Dict]:
        """Predict churn risk for multiple customers/contacts"""
        db = get_db()
        cursor = db.cursor()
        
        if not contact_ids:
            # Get all customers
            cursor.execute("SELECT id FROM customers WHERE status != 'inactive' AND status != 'lost'")
            contact_ids = [row[0] for row in cursor.fetchall()]
        
        predictions = []
        for contact_id in contact_ids[:50]:  # Limit to 50 for performance
            prediction = self.predict_churn_risk(contact_id=contact_id)
            if 'error' not in prediction:
                predictions.append(prediction)
        
        # Sort by risk score descending (highest risk first)
        predictions.sort(key=lambda x: x['churn_risk_score'], reverse=True)
        
        return predictions
