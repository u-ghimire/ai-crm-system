# AI-Powered Company Size Estimation - Test Documentation

## Overview

This test suite validates the AI-powered company size estimation feature in the Lead Scoring module. The feature enhances lead scoring by using OpenAI's GPT model to estimate company size based on company name and website, with a robust fallback to heuristic-based estimation.

## Running the Tests

```bash
cd ai-crm-system/backend
python test_lead_scoring_ai.py
```

## Test Coverage

### 1. Heuristic Fallback Tests
Validates that the system works correctly when OpenAI API is not available:
- Large enterprises (keywords: enterprise, global, international, corporation) → Score: 90
- Registered companies (keywords: inc, llc, ltd, company) → Score: 70  
- Startups (keywords: startup, ventures) → Score: 50
- Generic companies → Score: 40
- Empty/missing company name → Score: 30

### 2. Website Parameter Tests
Verifies that the website parameter is properly handled:
- Method accepts website parameter
- Method works without website parameter (None)
- No errors occur in either case

### 3. Integration Tests
Ensures the updated method integrates properly with the calculate_score method:
- Customer with website field is processed correctly
- Customer without website field is processed correctly
- Lead scores remain within valid range (0-100)

### 4. OpenAI API Handling Tests
Tests behavior with and without OpenAI API key:
- Gracefully handles missing API key
- Falls back to heuristic when API fails
- Handles API errors without crashing

## Implementation Details

### Method Signature
```python
def _calculate_company_size_score(self, company: str, website: str = None) -> float
```

### AI Estimation Flow
1. Check if OPENAI_API_KEY is set and valid
2. If yes, attempt AI estimation:
   - Send company name and website to GPT-3.5-turbo
   - Parse response for size category: Large Enterprise, Medium Business, Small Business, or Startup
   - Map category to score: 90, 70, 50, or 40 respectively
3. If AI fails or API key not set, fall back to heuristic:
   - Check company name for size-indicating keywords
   - Return appropriate score based on keywords

### Fallback Heuristic
The heuristic ensures the system always works, even without an API key:
- **Large Enterprise** (90): Contains 'enterprise', 'global', 'international', 'corporation'
- **Registered Company** (70): Contains 'inc', 'llc', 'ltd', 'company'
- **Startup** (50): Contains 'startup', 'ventures'
- **Generic** (40): Any other company name
- **Missing** (30): Empty or None company name

## Environment Variables

### OPENAI_API_KEY
Set this environment variable to enable AI-powered estimation:

```bash
export OPENAI_API_KEY="sk-..."
```

If not set or set to the default placeholder, the system will use heuristic fallback only.

## Expected Test Results

```
======================================================================
Lead Scoring - AI-Powered Company Size Estimation Test Suite
======================================================================

=== Testing Heuristic Fallback ===
  ✓ 'Global Enterprise Corporation' -> 90 (Large Enterprise keywords)
  ✓ 'International Corporation' -> 90 (Large Enterprise keywords)
  ✓ 'Acme Inc' -> 70 (Inc/LLC/Ltd keywords)
  ✓ 'Tech Company LLC' -> 70 (Inc/LLC/Ltd keywords)
  ✓ 'Tech Startup Ventures' -> 50 (Startup keywords)
  ✓ 'New Ventures' -> 50 (Startup keywords)
  ✓ 'Local Shop' -> 40 (Generic company)
  ✓ '' -> 30 (Empty company name)

=== Testing Website Parameter ===
  ✓ With website: Score = 70
  ✓ Without website: Score = 70

=== Testing Integration with calculate_score ===
  ✓ Customer with website: Lead Score = 69.0
  ✓ Customer without website: Lead Score = 42.25

=== Testing OpenAI API Key Handling ===
  ℹ OPENAI_API_KEY is not set
    Using heuristic fallback only
  ✓ Microsoft Corporation -> Score: 90
  ✓ Unknown company handled gracefully: Score = 70

======================================================================
Test Results: 14 passed, 0 failed
ALL TESTS PASSED ✓
======================================================================
```

## Integration with Backend API

The feature is automatically integrated with the customer creation and update endpoints:

### POST /api/customers
When creating a customer, include the `website` field to enable AI-powered estimation:

```json
{
  "name": "John Doe",
  "company": "Microsoft Corporation",
  "website": "https://microsoft.com",
  "industry": "technology",
  "budget": 100000,
  "status": "interested"
}
```

The lead score will be calculated automatically, including the company size component.

### PUT /api/customers/:id
When updating a customer, the lead score is recalculated with the latest company and website information.

## Benefits

1. **More Accurate Scoring**: AI can recognize company sizes better than keyword matching
2. **Graceful Degradation**: Works without API key via fallback heuristic
3. **Zero Breaking Changes**: Existing code continues to work unchanged
4. **Enhanced Data**: Website field adds context for better estimation
5. **Cost Efficient**: Uses minimal tokens (10 max) for quick responses

## Troubleshooting

### Tests Fail with API Error
- Ensure OPENAI_API_KEY is valid if set
- Tests should pass even without API key (using fallback)
- Check internet connectivity if API key is set

### Unexpected Scores
- Verify company name contains expected keywords
- Check if API key is set and valid
- Review heuristic rules in code comments

### Import Errors
- Ensure openai package is installed: `pip install openai==0.28.0`
- Run from backend directory
- Check Python path includes backend modules
