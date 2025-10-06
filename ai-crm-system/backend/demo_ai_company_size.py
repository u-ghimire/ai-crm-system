#!/usr/bin/env python3
"""
Demo script showing AI-powered company size estimation in action

This script demonstrates both the heuristic fallback and AI-powered modes.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.lead_scoring import LeadScoring


def print_section(title):
    """Print a section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def demo_heuristic_mode():
    """Demonstrate heuristic-based estimation"""
    print_section("DEMO: Heuristic-Based Company Size Estimation")
    
    lead_scorer = LeadScoring()
    
    companies = [
        ("Google LLC", "https://google.com"),
        ("Microsoft Corporation", "https://microsoft.com"),
        ("Local Coffee Shop", None),
        ("Tech Startup Inc", "https://techstartup.io"),
        ("International Consulting Group", "https://icg.com"),
        ("Small Business Ventures", None)
    ]
    
    print("\nCompany Size Scoring (Heuristic Mode):")
    print("-" * 70)
    
    for company, website in companies:
        score = lead_scorer._calculate_company_size_score(company, website)
        website_str = website if website else "N/A"
        print(f"  {company:40} | Website: {website_str:25} | Score: {score}")


def demo_full_lead_scoring():
    """Demonstrate full lead scoring with company size component"""
    print_section("DEMO: Complete Lead Scoring with Company Size")
    
    lead_scorer = LeadScoring()
    
    customers = [
        {
            'name': 'Alice Johnson',
            'company': 'Microsoft Corporation',
            'website': 'https://microsoft.com',
            'industry': 'technology',
            'budget': 100000,
            'status': 'hot',
            'notes': 'CTO interested in enterprise plan'
        },
        {
            'name': 'Bob Smith',
            'company': 'Small Coffee LLC',
            'industry': 'retail',
            'budget': 5000,
            'status': 'lead'
        },
        {
            'name': 'Charlie Brown',
            'company': 'Startup Ventures',
            'website': 'https://startupventures.io',
            'industry': 'technology',
            'budget': 25000,
            'status': 'interested',
            'notes': 'CEO looking for solution'
        }
    ]
    
    print("\nComplete Lead Scoring Results:")
    print("-" * 70)
    
    for customer in customers:
        lead_score = lead_scorer.calculate_score(customer)
        insights = lead_scorer.get_insights(customer)
        
        print(f"\n  Customer: {customer['name']}")
        print(f"    Company: {customer['company']}")
        print(f"    Website: {customer.get('website', 'N/A')}")
        print(f"    Industry: {customer['industry']}")
        print(f"    Budget: ${customer['budget']:,}")
        print(f"    Status: {customer['status']}")
        print(f"    → Lead Score: {lead_score}/100")
        print(f"    → Grade: {insights['grade']}")
        print(f"    → Priority: {insights['priority']}")
        print(f"    → Conversion Probability: {insights['conversion_probability']}%")


def demo_ai_mode_simulation():
    """Show what AI mode would look like if enabled"""
    print_section("DEMO: AI Mode (Simulated)")
    
    print("\nWhen OPENAI_API_KEY is set, the system will:")
    print("  1. Send company name and website to OpenAI GPT-3.5-turbo")
    print("  2. Receive intelligent size category estimation")
    print("  3. Map category to score (90, 70, 50, or 40)")
    print("  4. Fall back to heuristic if API call fails")
    
    print("\nExample AI Analysis:")
    print("-" * 70)
    
    examples = [
        ("Amazon", "https://amazon.com", "Large Enterprise", 90),
        ("Shopify", "https://shopify.com", "Medium Business", 70),
        ("Local Bakery", None, "Small Business", 50),
        ("Y Combinator Startup", "https://example.com", "Startup", 40)
    ]
    
    for company, website, ai_category, score in examples:
        website_str = website if website else "N/A"
        print(f"  {company:30} | {website_str:25}")
        print(f"    → AI Category: {ai_category:20} | Score: {score}")
        print()


def show_configuration():
    """Show current configuration"""
    print_section("CONFIGURATION")
    
    api_key = os.environ.get('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')
    
    print("\nCurrent Setup:")
    print(f"  OPENAI_API_KEY: ", end="")
    if api_key and api_key != 'YOUR_OPENAI_API_KEY_HERE':
        print(f"Set (length: {len(api_key)} chars)")
        print("  Mode: AI-Powered with Heuristic Fallback")
    else:
        print("Not set")
        print("  Mode: Heuristic Only")
    
    print("\nTo enable AI mode:")
    print("  export OPENAI_API_KEY='sk-...'")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("  AI-POWERED COMPANY SIZE ESTIMATION - DEMONSTRATION")
    print("="*70)
    
    show_configuration()
    demo_heuristic_mode()
    demo_full_lead_scoring()
    demo_ai_mode_simulation()
    
    print("\n" + "="*70)
    print("  DEMONSTRATION COMPLETE")
    print("="*70 + "\n")
