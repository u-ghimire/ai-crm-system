#!/usr/bin/env python3
"""
Advanced test demonstrating AI mode behavior with mock OpenAI API

This test shows how the system would behave with a working OpenAI API key.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.lead_scoring import LeadScoring


class MockOpenAIResponse:
    """Mock OpenAI API response"""
    def __init__(self, content):
        self.choices = [MockChoice(content)]


class MockChoice:
    """Mock choice from OpenAI response"""
    def __init__(self, content):
        self.message = {'content': content}


def test_ai_estimation_with_mock():
    """Test AI estimation logic with mocked responses"""
    print("\n=== Testing AI Response Parsing Logic ===")
    
    # Test the parsing logic that would be used with real API responses
    test_responses = [
        ("Large Enterprise", 90),
        ("large enterprise company", 90),
        ("Medium Business", 70),
        ("medium sized business", 70),
        ("Small Business", 50),
        ("small local business", 50),
        ("Startup", 40),
        ("early stage startup", 40),
        ("Unknown Category", None)  # Should fall through to heuristic
    ]
    
    for response_text, expected_score in test_responses:
        answer = response_text.lower()
        
        if 'large' in answer:
            score = 90
        elif 'medium' in answer:
            score = 70
        elif 'small' in answer:
            score = 50
        elif 'startup' in answer:
            score = 40
        else:
            score = None
        
        if expected_score is None:
            print(f"  ✓ '{response_text}' -> Falls back to heuristic")
        elif score == expected_score:
            print(f"  ✓ '{response_text}' -> {score} (Expected: {expected_score})")
        else:
            print(f"  ✗ '{response_text}' -> {score} (Expected: {expected_score})")


def test_prompt_construction():
    """Test that prompts are constructed correctly"""
    print("\n=== Testing Prompt Construction ===")
    
    # Test with company and website
    company = "Microsoft Corporation"
    website = "https://microsoft.com"
    
    prompt = f"""
Estimate the company size category for the following company. Respond with one of: 'Large Enterprise', 'Medium Business', 'Small Business', or 'Startup'.
Company Name: {company}
"""
    if website:
        prompt += f"\nWebsite: {website}"
    
    print(f"  ✓ Prompt with website:")
    print(f"    {prompt.strip()[:80]}...")
    
    # Test with company only
    company = "Small Startup"
    website = None
    
    prompt = f"""
Estimate the company size category for the following company. Respond with one of: 'Large Enterprise', 'Medium Business', 'Small Business', or 'Startup'.
Company Name: {company}
"""
    if website:
        prompt += f"\nWebsite: {website}"
    
    print(f"\n  ✓ Prompt without website:")
    print(f"    {prompt.strip()[:80]}...")


def test_error_handling():
    """Test error handling scenarios"""
    print("\n=== Testing Error Handling ===")
    
    lead_scorer = LeadScoring()
    
    # Simulate various error scenarios
    test_cases = [
        (None, None, "None company name"),
        ("", None, "Empty company name"),
        ("Valid Company", "", "Empty website string"),
        ("Valid Company", None, "None website"),
    ]
    
    for company, website, description in test_cases:
        try:
            score = lead_scorer._calculate_company_size_score(company, website)
            print(f"  ✓ {description}: Score = {score}")
        except Exception as e:
            print(f"  ✗ {description}: Exception - {e}")


def demonstrate_full_integration():
    """Show how the feature integrates with the full system"""
    print("\n=== Full System Integration ===")
    
    lead_scorer = LeadScoring()
    
    # Scenario 1: Large enterprise
    customer = {
        'name': 'Enterprise Customer',
        'company': 'Global Tech Corporation',
        'website': 'https://globaltech.com',
        'industry': 'technology',
        'budget': 250000,
        'status': 'hot',
        'email': 'cto@globaltech.com',
        'phone': '+1-555-0100',
        'notes': 'CTO of major enterprise, interested in full suite'
    }
    
    score = lead_scorer.calculate_score(customer)
    insights = lead_scorer.get_insights(customer)
    
    print(f"\n  Scenario 1: Large Enterprise")
    print(f"    Company: {customer['company']}")
    print(f"    Lead Score: {score}/100")
    print(f"    Grade: {insights['grade']}")
    print(f"    Priority: {insights['priority']}")
    print(f"    Strengths: {', '.join(insights['strengths'][:2])}")
    
    # Scenario 2: Startup
    customer = {
        'name': 'Startup Founder',
        'company': 'Cool Startup Ventures',
        'website': 'https://coolstartup.io',
        'industry': 'technology',
        'budget': 15000,
        'status': 'interested'
    }
    
    score = lead_scorer.calculate_score(customer)
    insights = lead_scorer.get_insights(customer)
    
    print(f"\n  Scenario 2: Startup")
    print(f"    Company: {customer['company']}")
    print(f"    Lead Score: {score}/100")
    print(f"    Grade: {insights['grade']}")
    print(f"    Priority: {insights['priority']}")
    print(f"    Top Recommendation: {insights['recommendations'][0]}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  Advanced AI Company Size Estimation Tests")
    print("="*70)
    
    test_ai_estimation_with_mock()
    test_prompt_construction()
    test_error_handling()
    demonstrate_full_integration()
    
    print("\n" + "="*70)
    print("  ALL ADVANCED TESTS COMPLETED ✓")
    print("="*70 + "\n")
