# modules/sales_forecasting.py
"""
Sales Forecasting Module - AI-powered sales prediction
Uses historical data and ML models to forecast future sales
"""

import json
from typing import Dict, List, Any
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
import random

class SalesForecasting:
    def __init__(self):
        """Initialize sales forecasting system"""
        self.forecast_models = {
            'linear': self._linear_forecast,
            'seasonal': self._seasonal_forecast,
            'ai_enhanced': self._ai_enhanced_forecast
        }
    
    def generate_forecast(self, timeframe: str = 'monthly', historical_data: List = None) -> Dict:
        """Generate sales forecast for specified timeframe"""
        # Get or generate historical data
        if not historical_data:
            historical_data = self._generate_sample_historical_data()
        
        # Calculate forecasts using different models
        forecasts = {}
        for model_name, model_func in self.forecast_models.items():
            forecasts[model_name] = model_func(historical_data, timeframe)
        
        # Combine forecasts for ensemble prediction
        ensemble_forecast = self._ensemble_forecast(forecasts)
        
        # Generate insights
        insights = self._generate_forecast_insights(ensemble_forecast, historical_data)
        
        return {
            'timeframe': timeframe,
            'forecast': ensemble_forecast,
            'confidence_interval': self._calculate_confidence_interval(ensemble_forecast),
            'insights': insights,
            'individual_models': forecasts,
            'generated_at': datetime.now().isoformat()
        }
    
    def get_quick_forecast(self) -> Dict:
        """Get quick forecast summary for dashboard"""
        forecast = self.generate_forecast('monthly')
        
        return {
            'next_month': forecast['forecast']['next_period'],
            'quarter': forecast['forecast']['quarter'],
            'year': forecast['forecast']['year'],
            'trend': forecast['insights']['trend'],
            'confidence': forecast['confidence_interval']['confidence_level']
        }
    
    def _generate_sample_historical_data(self) -> List[Dict]:
        """Generate sample historical sales data"""
        data = []
        base_value = 50000
        
        for i in range(12):
            # Add some seasonality and trend
            month_value = base_value + (i * 2000)  # Growth trend
            month_value += np.sin(i * np.pi / 6) * 10000  # Seasonality
            month_value += random.gauss(0, 5000)  # Random noise
            
            data.append({
                'period': (datetime.now() - timedelta(days=30 * (12 - i))).strftime('%Y-%m'),
                'revenue': max(0, month_value),
                'deals_closed': int(month_value / 10000),
                'conversion_rate': 0.15 + random.uniform(-0.05, 0.05)
            })
        
        return data
    
    def _linear_forecast(self, historical_data: List[Dict], timeframe: str) -> Dict:
        """Linear regression forecast"""
        # Extract revenue values
        revenues = [d['revenue'] for d in historical_data]
        x = np.arange(len(revenues))
        
        # Fit linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, revenues)
        
        # Generate forecast
        forecast_periods = self._get_forecast_periods(timeframe)
        forecasts = {}
        
        for period_name, periods_ahead in forecast_periods.items():
            forecast_x = len(revenues) + periods_ahead
            forecast_value = slope * forecast_x + intercept
            forecasts[period_name] = max(0, forecast_value)
        
        return {
            'model': 'linear',
            'forecasts': forecasts,
            'trend': 'increasing' if slope > 0 else 'decreasing',
            'r_squared': r_value ** 2
        }
    
    def _seasonal_forecast(self, historical_data: List[Dict], timeframe: str) -> Dict:
        """Seasonal decomposition forecast"""
        revenues = [d['revenue'] for d in historical_data]
        
        # Simple seasonal decomposition
        season_length = 4  # Quarterly seasonality
        seasonal_factors = self._calculate_seasonal_factors(revenues, season_length)
        
        # Calculate trend
        trend = np.mean(revenues[-3:]) - np.mean(revenues[:3])
        
        forecast_periods = self._get_forecast_periods(timeframe)
        forecasts = {}
        
        base_forecast = np.mean(revenues[-3:])
        
        for period_name, periods_ahead in forecast_periods.items():
            # Apply trend
            forecast = base_forecast + (trend * periods_ahead / 12)
            
            # Apply seasonality
            season_index = (len(revenues) + periods_ahead) % season_length
            forecast *= seasonal_factors[season_index]
            
            forecasts[period_name] = max(0, forecast)
        
        return {
            'model': 'seasonal',
            'forecasts': forecasts,
            'seasonal_factors': seasonal_factors.tolist(),
            'trend_component': trend
        }
    
    def _ai_enhanced_forecast(self, historical_data: List[Dict], timeframe: str) -> Dict:
        """AI-enhanced forecast using multiple factors"""
        revenues = [d['revenue'] for d in historical_data]
        deals = [d['deals_closed'] for d in historical_data]
        conversion_rates = [d['conversion_rate'] for d in historical_data]
        
        # Calculate growth rates
        revenue_growth = np.mean(np.diff(revenues) / revenues[:-1]) if len(revenues) > 1 else 0.05
        deal_growth = np.mean(np.diff(deals) / deals[:-1]) if len(deals) > 1 else 0.03
        
        # Calculate average metrics
        avg_revenue_per_deal = np.mean([r/d for r, d in zip(revenues, deals) if d > 0])
        avg_conversion_rate = np.mean(conversion_rates)
        
        forecast_periods = self._get_forecast_periods(timeframe)
        forecasts = {}
        
        base_revenue = revenues[-1] if revenues else 50000
        base_deals = deals[-1] if deals else 5
        
        for period_name, periods_ahead in forecast_periods.items():
            # Project deals
            projected_deals = base_deals * ((1 + deal_growth) ** (periods_ahead / 12))
            
            # Project revenue per deal with improvement factor
            improvement_factor = 1 + (0.02 * periods_ahead / 12)  # 2% annual improvement
            projected_revenue_per_deal = avg_revenue_per_deal * improvement_factor
            
            # Calculate forecast
            forecast = projected_deals * projected_revenue_per_deal
            
            # Apply conversion rate adjustment
            conversion_adjustment = 1 + ((avg_conversion_rate - 0.15) * 2)  # Baseline 15%
            forecast *= conversion_adjustment
            
            forecasts[period_name] = max(0, forecast)
        
        return {
            'model': 'ai_enhanced',
            'forecasts': forecasts,
            'factors': {
                'revenue_growth_rate': revenue_growth,
                'deal_growth_rate': deal_growth,
                'avg_deal_value': avg_revenue_per_deal,
                'conversion_rate': avg_conversion_rate
            }
        }
    
    def _ensemble_forecast(self, forecasts: Dict) -> Dict:
        """Combine multiple forecasts for ensemble prediction"""
        ensemble = {}
        weights = {
            'linear': 0.25,
            'seasonal': 0.35,
            'ai_enhanced': 0.40
        }
        
        # Get all forecast periods
        periods = set()
        for model_forecast in forecasts.values():
            periods.update(model_forecast['forecasts'].keys())
        
        # Calculate weighted average for each period
        for period in periods:
            weighted_sum = 0
            total_weight = 0
            
            for model_name, weight in weights.items():
                if model_name in forecasts and period in forecasts[model_name]['forecasts']:
                    weighted_sum += forecasts[model_name]['forecasts'][period] * weight
                    total_weight += weight
            
            if total_weight > 0:
                ensemble[period] = weighted_sum / total_weight
        
        return ensemble
    
    def _calculate_confidence_interval(self, forecast: Dict, confidence: float = 0.95) -> Dict:
        """Calculate confidence intervals for forecasts"""
        intervals = {}
        
        for period, value in forecast.items():
            # Simple confidence interval calculation
            # In production, this would use historical error rates
            std_error = value * 0.1  # 10% standard error
            z_score = stats.norm.ppf((1 + confidence) / 2)
            
            intervals[period] = {
                'forecast': value,
                'lower': max(0, value - z_score * std_error),
                'upper': value + z_score * std_error
            }
        
        return {
            'intervals': intervals,
            'confidence_level': confidence
        }
    
    def _generate_forecast_insights(self, forecast: Dict, historical_data: List[Dict]) -> Dict:
        """Generate insights from forecast"""
        insights = {
            'trend': self._determine_trend(forecast),
            'seasonality': self._detect_seasonality(historical_data),
            'risk_factors': self._identify_risk_factors(forecast, historical_data),
            'opportunities': self._identify_opportunities(forecast, historical_data),
            'recommendations': self._generate_recommendations(forecast, historical_data)
        }
        
        return insights
    
    def _determine_trend(self, forecast: Dict) -> str:
        """Determine overall trend from forecast"""
        values = list(forecast.values())
        if not values:
            return 'stable'
        
        if len(values) > 1:
            if values[-1] > values[0] * 1.1:
                return 'strong_growth'
            elif values[-1] > values[0]:
                return 'moderate_growth'
            elif values[-1] < values[0] * 0.9:
                return 'declining'
        
        return 'stable'
    
    def _detect_seasonality(self, historical_data: List[Dict]) -> Dict:
        """Detect seasonal patterns in historical data"""
        if len(historical_data) < 4:
            return {'detected': False}
        
        revenues = [d['revenue'] for d in historical_data]
        
        # Simple seasonality detection
        seasonal_pattern = {
            'detected': True,
            'pattern': 'quarterly',
            'peak_periods': [],
            'low_periods': []
        }
        
        # Find peak and low periods
        mean_revenue = np.mean(revenues)
        for i, revenue in enumerate(revenues):
            if revenue > mean_revenue * 1.1:
                seasonal_pattern['peak_periods'].append(i % 12 + 1)  # Month number
            elif revenue < mean_revenue * 0.9:
                seasonal_pattern['low_periods'].append(i % 12 + 1)
        
        return seasonal_pattern
    
    def _identify_risk_factors(self, forecast: Dict, historical_data: List[Dict]) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        # Check for high variability
        revenues = [d['revenue'] for d in historical_data]
        if revenues:
            cv = np.std(revenues) / np.mean(revenues)  # Coefficient of variation
            if cv > 0.3:
                risks.append("High revenue variability detected")
        
        # Check conversion rate trends
        conversion_rates = [d['conversion_rate'] for d in historical_data]
        if len(conversion_rates) > 3:
            recent_avg = np.mean(conversion_rates[-3:])
            overall_avg = np.mean(conversion_rates)
            if recent_avg < overall_avg * 0.9:
                risks.append("Declining conversion rates")
        
        # Check forecast reliability
        if 'next_period' in forecast and 'quarter' in forecast:
            if forecast['quarter'] < forecast['next_period'] * 3:
                risks.append("Potential over-optimistic short-term forecast")
        
        return risks if risks else ["No significant risks identified"]
    
    def _identify_opportunities(self, forecast: Dict, historical_data: List[Dict]) -> List[str]:
        """Identify growth opportunities"""
        opportunities = []
        
        # Check growth trajectory
        if 'year' in forecast and 'next_period' in forecast:
            annual_growth = (forecast['year'] - forecast['next_period'] * 12) / (forecast['next_period'] * 12)
            if annual_growth > 0.2:
                opportunities.append("Strong growth trajectory projected")
        
        # Check conversion rate potential
        conversion_rates = [d['conversion_rate'] for d in historical_data]
        if conversion_rates and max(conversion_rates) > np.mean(conversion_rates) * 1.2:
            opportunities.append("Conversion rate optimization potential")
        
        # Check deal size trends
        if len(historical_data) > 3:
            recent_deals = [d['deals_closed'] for d in historical_data[-3:]]
            if all(recent_deals[i] <= recent_deals[i+1] for i in range(len(recent_deals)-1)):
                opportunities.append("Increasing deal velocity trend")
        
        return opportunities if opportunities else ["Focus on consistent execution"]
    
    def _generate_recommendations(self, forecast: Dict, historical_data: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        trend = self._determine_trend(forecast)
        
        if trend == 'strong_growth':
            recommendations.append("Scale sales team to capture growth opportunity")
            recommendations.append("Invest in automation to maintain quality at scale")
        elif trend == 'declining':
            recommendations.append("Review and optimize sales process")
            recommendations.append("Focus on customer retention and upselling")
        else:
            recommendations.append("Maintain current strategy with incremental improvements")
            recommendations.append("Focus on conversion rate optimization")
        
        # Add specific recommendations based on data
        conversion_rates = [d['conversion_rate'] for d in historical_data]
        if conversion_rates and np.mean(conversion_rates) < 0.15:
            recommendations.append("Implement lead qualification improvements")
        
        revenues = [d['revenue'] for d in historical_data]
        deals = [d['deals_closed'] for d in historical_data]
        if revenues and deals:
            avg_deal_size = np.mean([r/d for r, d in zip(revenues, deals) if d > 0])
            if avg_deal_size < 10000:
                recommendations.append("Focus on enterprise accounts for larger deal sizes")
        
        return recommendations[:4]  # Return top 4 recommendations
    
    def _calculate_seasonal_factors(self, data: List[float], season_length: int) -> np.ndarray:
        """Calculate seasonal factors from data"""
        if len(data) < season_length:
            return np.ones(season_length)
        
        # Group data by season
        seasonal_avgs = np.zeros(season_length)
        counts = np.zeros(season_length)
        
        for i, value in enumerate(data):
            season_idx = i % season_length
            seasonal_avgs[season_idx] += value
            counts[season_idx] += 1
        
        # Calculate factors
        seasonal_avgs = seasonal_avgs / (counts + 1e-10)  # Avoid division by zero
        overall_avg = np.mean(data)
        
        factors = seasonal_avgs / (overall_avg + 1e-10)
        
        # Normalize factors
        factors = factors / np.mean(factors)
        
        return factors
    
    def _get_forecast_periods(self, timeframe: str) -> Dict[str, int]:
        """Get forecast periods based on timeframe"""
        if timeframe == 'daily':
            return {
                'tomorrow': 1,
                'next_week': 7,
                'next_month': 30
            }
        elif timeframe == 'weekly':
            return {
                'next_week': 1,
                'next_month': 4,
                'quarter': 12
            }
        elif timeframe == 'monthly':
            return {
                'next_period': 1,
                'quarter': 3,
                'year': 12
            }
        else:  # yearly
            return {
                'next_year': 1,
                'three_years': 3,
                'five_years': 5
            }