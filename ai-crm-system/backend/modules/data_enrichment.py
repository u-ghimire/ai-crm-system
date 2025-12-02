"""
Data Enrichment Service
Automatically enriches company and contact data with information from external sources
"""

import re
import requests
from typing import Dict, List, Optional, Any
from modules.groq_ai import GroqAI
from modules import db_helper

class DataEnrichment:
    def __init__(self):
        self.groq_ai = GroqAI()
        
        # Common social media URL patterns
        self.social_patterns = {
            'linkedin_personal': r'linkedin\.com/in/([a-zA-Z0-9-]+)',
            'linkedin_company': r'linkedin\.com/company/([a-zA-Z0-9-]+)',
            'twitter': r'twitter\.com/([a-zA-Z0-9_]+)',
            'facebook': r'facebook\.com/([a-zA-Z0-9.]+)',
            'github': r'github\.com/([a-zA-Z0-9-]+)'
        }
    
    def enrich_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich company data with additional information
        
        Args:
            company_data: Basic company info (name, website, etc.)
        
        Returns:
            Enhanced company data with industry, size, social profiles, etc.
        """
        try:
            enriched = company_data.copy()
            
            # Extract domain from website
            domain = self._extract_domain(company_data.get('website', ''))
            
            # Use AI to infer company details if minimal data provided
            if not company_data.get('industry') or not company_data.get('description'):
                ai_enrichment = self._ai_company_inference(
                    company_data.get('name'),
                    domain,
                    company_data.get('description', '')
                )
                enriched.update(ai_enrichment)
            
            # Extract social profiles from website if available
            if company_data.get('website'):
                social_profiles = self._extract_social_profiles(company_data['website'])
                enriched['social_profiles'] = social_profiles
            
            # Infer company size from available data
            if not company_data.get('size'):
                enriched['size'] = self._infer_company_size(enriched)
            
            # Generate company insights
            insights = self._generate_company_insights(enriched)
            enriched['insights'] = insights
            
            enriched['enriched'] = True
            enriched['enriched_at'] = self._get_timestamp()
            
            return {
                'success': True,
                'data': enriched,
                'fields_enriched': list(set(enriched.keys()) - set(company_data.keys()))
            }
            
        except Exception as e:
            print(f"Error enriching company: {e}")
            return {
                'success': False,
                'message': f"Failed to enrich company data: {str(e)}",
                'data': company_data
            }
    
    def enrich_contact(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich contact data with additional information
        
        Args:
            contact_data: Basic contact info (name, email, company, etc.)
        
        Returns:
            Enhanced contact data with job title inferences, social profiles, etc.
        """
        try:
            enriched = contact_data.copy()
            
            # Extract social profiles from any URLs in notes or linkedin_url field
            social_profiles = {}
            
            if contact_data.get('linkedin_url'):
                linkedin_username = self._extract_social_username(
                    contact_data['linkedin_url'], 
                    'linkedin_personal'
                )
                if linkedin_username:
                    social_profiles['linkedin'] = f"linkedin.com/in/{linkedin_username}"
            
            if contact_data.get('notes'):
                found_profiles = self._extract_social_profiles_from_text(contact_data['notes'])
                social_profiles.update(found_profiles)
            
            enriched['social_profiles'] = social_profiles
            
            # Infer job level and department from job title
            if contact_data.get('job_title'):
                job_insights = self._analyze_job_title(contact_data['job_title'])
                enriched['job_level'] = job_insights.get('level')
                enriched['department'] = job_insights.get('department')
                enriched['decision_maker'] = job_insights.get('is_decision_maker', False)
            
            # Use AI to enrich contact profile
            if contact_data.get('name') and contact_data.get('company'):
                ai_enrichment = self._ai_contact_inference(
                    contact_data['name'],
                    contact_data.get('job_title', ''),
                    contact_data.get('company', ''),
                    contact_data.get('industry', '')
                )
                enriched.update(ai_enrichment)
            
            # Validate and normalize email
            if contact_data.get('email'):
                email_validation = self._validate_email(contact_data['email'])
                enriched['email_valid'] = email_validation['valid']
                enriched['email_provider'] = email_validation['provider']
            
            # Normalize phone number
            if contact_data.get('phone'):
                enriched['phone_normalized'] = self._normalize_phone(contact_data['phone'])
            
            enriched['enriched'] = True
            enriched['enriched_at'] = self._get_timestamp()
            
            return {
                'success': True,
                'data': enriched,
                'fields_enriched': list(set(enriched.keys()) - set(contact_data.keys()))
            }
            
        except Exception as e:
            print(f"Error enriching contact: {e}")
            return {
                'success': False,
                'message': f"Failed to enrich contact data: {str(e)}",
                'data': contact_data
            }
    
    def auto_enrich_from_website(self, website_url: str) -> Dict[str, Any]:
        """
        Automatically extract company information from website
        """
        try:
            domain = self._extract_domain(website_url)
            
            # Use AI to analyze website and extract information
            prompt = f"""
Analyze this company website domain and provide structured information:

Website: {domain}

Based on the domain name and any knowledge you have, provide:

COMPANY_NAME: [most likely company name]
INDUSTRY: [primary industry/sector]
SIZE: [Startup/Small/Medium/Enterprise]
DESCRIPTION: [2-sentence description]
LIKELY_PRODUCTS: [what they likely offer]
TARGET_MARKET: [who they serve]
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=400)
            
            # Parse response
            company_info = {
                'name': self._extract_field(response, 'COMPANY_NAME'),
                'industry': self._extract_field(response, 'INDUSTRY'),
                'size': self._extract_field(response, 'SIZE'),
                'description': self._extract_field(response, 'DESCRIPTION'),
                'products': self._extract_field(response, 'LIKELY_PRODUCTS'),
                'target_market': self._extract_field(response, 'TARGET_MARKET'),
                'website': website_url,
                'auto_enriched': True
            }
            
            return {
                'success': True,
                'data': company_info,
                'confidence': 'medium'
            }
            
        except Exception as e:
            print(f"Error auto-enriching from website: {e}")
            return {
                'success': False,
                'message': f"Failed to extract data from website: {str(e)}"
            }
    
    def _ai_company_inference(self, company_name: str, domain: str, 
                            existing_description: str) -> Dict[str, Any]:
        """Use AI to infer company details"""
        try:
            prompt = f"""
Provide business intelligence for this company:

Company Name: {company_name}
Website Domain: {domain}
Existing Info: {existing_description}

Generate:
INDUSTRY: [primary industry]
SIZE: [Startup/Small/Medium/Enterprise]
DESCRIPTION: [professional 2-sentence description]
KEY_OFFERINGS: [main products/services]
TARGET_CUSTOMERS: [typical customer profile]
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=300)
            
            return {
                'industry': self._extract_field(response, 'INDUSTRY'),
                'size': self._extract_field(response, 'SIZE'),
                'description': self._extract_field(response, 'DESCRIPTION') or existing_description,
                'key_offerings': self._extract_field(response, 'KEY_OFFERINGS'),
                'target_customers': self._extract_field(response, 'TARGET_CUSTOMERS')
            }
            
        except Exception as e:
            print(f"Error in AI company inference: {e}")
            return {}
    
    def _ai_contact_inference(self, name: str, job_title: str, 
                            company: str, industry: str) -> Dict[str, Any]:
        """Use AI to infer contact details"""
        try:
            prompt = f"""
Analyze this business contact profile:

Name: {name}
Job Title: {job_title}
Company: {company}
Industry: {industry}

Provide:
SENIORITY_LEVEL: [Entry/Mid/Senior/Executive/C-Level]
LIKELY_PAIN_POINTS: [top 3 professional challenges]
COMMUNICATION_STYLE: [preferred communication approach]
BEST_CONTACT_TIME: [optimal time to reach out]
"""
            
            response = self.groq_ai.generate_completion(prompt, max_tokens=300)
            
            return {
                'seniority_level': self._extract_field(response, 'SENIORITY_LEVEL'),
                'likely_pain_points': self._extract_field(response, 'LIKELY_PAIN_POINTS'),
                'communication_preference': self._extract_field(response, 'COMMUNICATION_STYLE'),
                'best_contact_time': self._extract_field(response, 'BEST_CONTACT_TIME')
            }
            
        except Exception as e:
            print(f"Error in AI contact inference: {e}")
            return {}
    
    def _extract_domain(self, url: str) -> str:
        """Extract clean domain from URL"""
        if not url:
            return ''
        
        # Remove protocol
        domain = re.sub(r'https?://', '', url)
        # Remove www
        domain = re.sub(r'^www\.', '', domain)
        # Remove path
        domain = domain.split('/')[0]
        # Remove port
        domain = domain.split(':')[0]
        
        return domain.lower()
    
    def _extract_social_profiles(self, website: str) -> Dict[str, str]:
        """Extract social media profiles (mock implementation - would need web scraping)"""
        # In production, this would scrape the website for social links
        # For now, return empty dict - can be enhanced with actual scraping
        return {}
    
    def _extract_social_profiles_from_text(self, text: str) -> Dict[str, str]:
        """Extract social media URLs from text"""
        profiles = {}
        
        for platform, pattern in self.social_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                username = matches[0]
                if 'linkedin' in platform:
                    profiles['linkedin'] = f"linkedin.com/in/{username}" if 'personal' in platform else f"linkedin.com/company/{username}"
                elif platform == 'twitter':
                    profiles['twitter'] = f"twitter.com/{username}"
                elif platform == 'github':
                    profiles['github'] = f"github.com/{username}"
        
        return profiles
    
    def _extract_social_username(self, url: str, platform: str) -> Optional[str]:
        """Extract username from social media URL"""
        pattern = self.social_patterns.get(platform)
        if not pattern:
            return None
        
        match = re.search(pattern, url, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _analyze_job_title(self, job_title: str) -> Dict[str, Any]:
        """Analyze job title to extract insights"""
        job_title_lower = job_title.lower()
        
        # Determine seniority level
        level = 'Mid'
        if any(word in job_title_lower for word in ['ceo', 'cto', 'cfo', 'chief', 'president', 'vp', 'vice president']):
            level = 'C-Level'
        elif any(word in job_title_lower for word in ['director', 'head of', 'lead']):
            level = 'Senior'
        elif any(word in job_title_lower for word in ['manager', 'senior']):
            level = 'Senior'
        elif any(word in job_title_lower for word in ['junior', 'associate', 'assistant', 'coordinator']):
            level = 'Entry'
        
        # Determine department
        department = 'Other'
        if any(word in job_title_lower for word in ['engineer', 'developer', 'technical', 'technology', 'cto', 'it']):
            department = 'Engineering/IT'
        elif any(word in job_title_lower for word in ['sales', 'business development', 'account']):
            department = 'Sales'
        elif any(word in job_title_lower for word in ['marketing', 'content', 'brand']):
            department = 'Marketing'
        elif any(word in job_title_lower for word in ['finance', 'accounting', 'cfo']):
            department = 'Finance'
        elif any(word in job_title_lower for word in ['hr', 'human resources', 'people', 'talent']):
            department = 'HR'
        elif any(word in job_title_lower for word in ['operations', 'ops', 'coo']):
            department = 'Operations'
        
        # Decision maker status
        is_decision_maker = level in ['C-Level', 'Senior'] or any(word in job_title_lower for word in ['director', 'vp', 'president', 'chief', 'head'])
        
        return {
            'level': level,
            'department': department,
            'is_decision_maker': is_decision_maker
        }
    
    def _validate_email(self, email: str) -> Dict[str, Any]:
        """Validate and analyze email address"""
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        valid = bool(re.match(email_pattern, email))
        
        # Extract provider
        provider = 'unknown'
        if '@' in email:
            domain = email.split('@')[1].lower()
            if 'gmail' in domain:
                provider = 'gmail'
            elif 'outlook' in domain or 'hotmail' in domain or 'live' in domain:
                provider = 'outlook'
            elif 'yahoo' in domain:
                provider = 'yahoo'
            else:
                provider = 'corporate'
        
        return {
            'valid': valid,
            'provider': provider
        }
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        # Remove all non-numeric characters
        digits = re.sub(r'\D', '', phone)
        
        # Format based on length
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return original if can't normalize
    
    def _infer_company_size(self, company_data: Dict) -> str:
        """Infer company size from available data"""
        # Simple heuristic - can be enhanced
        revenue = company_data.get('revenue', 0)
        
        if revenue > 1000000000:  # > $1B
            return 'Enterprise'
        elif revenue > 100000000:  # > $100M
            return 'Large'
        elif revenue > 10000000:  # > $10M
            return 'Medium'
        elif revenue > 1000000:  # > $1M
            return 'Small'
        else:
            return 'Startup'
    
    def _generate_company_insights(self, company_data: Dict) -> List[str]:
        """Generate actionable insights about company"""
        insights = []
        
        if company_data.get('industry'):
            insights.append(f"Operates in {company_data['industry']} industry")
        
        if company_data.get('size'):
            insights.append(f"{company_data['size']}-sized organization")
        
        if company_data.get('revenue'):
            insights.append(f"Revenue: ${company_data['revenue']:,.0f}")
        
        return insights
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract field value from AI response"""
        try:
            if field_name not in text:
                return ''
            
            lines = text.split('\n')
            for line in lines:
                if field_name in line and ':' in line:
                    value = line.split(':', 1)[1].strip()
                    # Remove brackets or quotes
                    value = re.sub(r'[\[\]\"]', '', value)
                    return value
            
            return ''
        except Exception:
            return ''
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
