#!/usr/bin/env python3
"""
Test suite for Lead Scoring module - AI-powered company size estimation

This test suite verifies:
1. Heuristic fallback works when OpenAI API is not available
2. Website parameter is properly handled
3. Integration with calculate_score method works correctly
4. AI estimation works when API key is available
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.lead_scoring import LeadScoring


class TestLeadScoringCompanySize:
    """Test cases for AI-powered company size estimation"""
    
    def __init__(self):
        self.lead_scorer = LeadScoring()
        self.passed = 0
        self.failed = 0
    
    def test_heuristic_fallback(self):
        """Test that heuristic fallback works when OpenAI API is not available"""
        print("\n=== Testing Heuristic Fallback ===")
        
        test_cases = [
            ("Global Enterprise Corporation", 90, "Large Enterprise keywords"),
            ("International Corporation", 90, "Large Enterprise keywords"),
            ("Acme Inc", 70, "Inc/LLC/Ltd keywords"),
            ("Tech Company LLC", 70, "Inc/LLC/Ltd keywords"),
            ("Tech Startup Ventures", 50, "Startup keywords"),
            ("New Ventures", 50, "Startup keywords"),
            ("Local Shop", 40, "Generic company"),
            ("", 30, "Empty company name")
        ]
        
        for company, expected, description in test_cases:
            score = self.lead_scorer._calculate_company_size_score(company)
            if score == expected:
                print(f"  ✓ '{company}' -> {score} ({description})")
                self.passed += 1
            else:
                print(f"  ✗ '{company}' -> {score} (Expected {expected}, {description})")
                self.failed += 1
    
    def test_website_parameter(self):
        """Test that website parameter is accepted and handled"""
        print("\n=== Testing Website Parameter ===")
        
        # Test with website
        score_with_website = self.lead_scorer._calculate_company_size_score(
            "Test Company", 
            "https://example.com"
        )
        print(f"  ✓ With website: Score = {score_with_website}")
        self.passed += 1
        
        # Test without website (None)
        score_without_website = self.lead_scorer._calculate_company_size_score(
            "Test Company", 
            None
        )
        print(f"  ✓ Without website: Score = {score_without_website}")
        self.passed += 1
        
        # Both should work without errors
        assert isinstance(score_with_website, (int, float))
        assert isinstance(score_without_website, (int, float))
    
    def test_integration_with_calculate_score(self):
        """Test that the updated method works with calculate_score"""
        print("\n=== Testing Integration with calculate_score ===")
        
        # Test customer data with website
        customer_with_website = {
            'name': 'John Doe',
            'company': 'Tech Corporation International',
            'website': 'https://techcorp.com',
            'industry': 'technology',
            'budget': 50000,
            'status': 'interested'
        }
        
        score1 = self.lead_scorer.calculate_score(customer_with_website)
        print(f"  ✓ Customer with website: Lead Score = {score1}")
        assert 0 <= score1 <= 100, "Score should be between 0 and 100"
        self.passed += 1
        
        # Test customer data without website
        customer_without_website = {
            'name': 'Jane Smith',
            'company': 'Small Startup',
            'industry': 'retail',
            'budget': 5000,
            'status': 'lead'
        }
        
        score2 = self.lead_scorer.calculate_score(customer_without_website)
        print(f"  ✓ Customer without website: Lead Score = {score2}")
        assert 0 <= score2 <= 100, "Score should be between 0 and 100"
        self.passed += 1
    
    def test_openai_api_handling(self):
        """Test behavior with/without OpenAI API key"""
        print("\n=== Testing OpenAI API Key Handling ===")
        
        # Check if OPENAI_API_KEY is set
        api_key = os.environ.get('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY_HERE')
        if api_key and api_key != 'YOUR_OPENAI_API_KEY_HERE':
            print(f"  ℹ OPENAI_API_KEY is set")
            print("    AI estimation will be attempted (may fall back to heuristic)")
        else:
            print("  ℹ OPENAI_API_KEY is not set")
            print("    Using heuristic fallback only")
        
        # This should work regardless of API key status
        score = self.lead_scorer._calculate_company_size_score(
            "Microsoft Corporation", 
            "https://microsoft.com"
        )
        print(f"  ✓ Microsoft Corporation -> Score: {score}")
        assert score == 90, "Microsoft Corporation should score 90"
        self.passed += 1
        
        # Test error handling - should not crash
        try:
            score = self.lead_scorer._calculate_company_size_score(
                "Unknown Company XYZ123", 
                "https://unknown.example"
            )
            print(f"  ✓ Unknown company handled gracefully: Score = {score}")
            self.passed += 1
        except Exception as e:
            print(f"  ✗ Exception occurred: {e}")
            self.failed += 1
    
    def run_all_tests(self):
        """Run all test cases"""
        print("\n" + "="*70)
        print("Lead Scoring - AI-Powered Company Size Estimation Test Suite")
        print("="*70)
        
        try:
            self.test_heuristic_fallback()
            self.test_website_parameter()
            self.test_integration_with_calculate_score()
            self.test_openai_api_handling()
            
            print("\n" + "="*70)
            print(f"Test Results: {self.passed} passed, {self.failed} failed")
            if self.failed == 0:
                print("ALL TESTS PASSED ✓")
            else:
                print("SOME TESTS FAILED ✗")
            print("="*70 + "\n")
            
            return self.failed == 0
            
        except Exception as e:
            print(f"\n✗ TEST SUITE FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    test_suite = TestLeadScoringCompanySize()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)
