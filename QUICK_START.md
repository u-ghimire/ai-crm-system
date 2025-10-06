# AI Company Size Estimation - Quick Start Guide

## What Was Implemented

AI-powered company size estimation in the lead scoring system. The system now intelligently estimates company size using OpenAI when available, with a reliable heuristic fallback.

## Quick Start

### 1. Enable AI Mode (Optional)

```bash
export OPENAI_API_KEY='sk-your-api-key-here'
```

Without this, the system uses heuristic fallback (still works perfectly).

### 2. Run Tests

```bash
cd ai-crm-system/backend
python test_lead_scoring_ai.py
```

Expected: "ALL TESTS PASSED ✓"

### 3. See Demo

```bash
python demo_ai_company_size.py
```

### 4. Use in API

When creating/updating customers, include the `website` field:

```json
{
  "company": "Microsoft Corporation",
  "website": "https://microsoft.com"
}
```

The lead score will automatically include the improved company size estimate.

## Files Changed

- `modules/lead_scoring.py` - Updated `_calculate_company_size_score` method
- `test_lead_scoring_ai.py` - Comprehensive test suite (14 tests)
- `test_advanced_ai.py` - Advanced edge case tests
- `demo_ai_company_size.py` - Interactive demonstration
- `TEST_README.md` - Complete documentation
- `IMPLEMENTATION_SUMMARY.md` - Implementation details

## How It Works

### With OpenAI API Key (AI Mode)
1. Sends company name + website to GPT-3.5-turbo
2. Gets intelligent size category
3. Maps to score (90, 70, 50, or 40)

### Without API Key (Heuristic Mode)
1. Analyzes company name keywords
2. Returns score based on patterns
3. Same score ranges as AI mode

## Scoring

- **90** - Large Enterprise
- **70** - Medium Business  
- **50** - Small Business / Startup
- **40** - Unknown / Generic
- **30** - Missing company

## Key Benefits

✅ More accurate lead scoring
✅ Works without OpenAI (heuristic fallback)
✅ No breaking changes
✅ Cost efficient (~$0.000015 per request)
✅ All tests passing

## Testing Status

- ✅ 14 basic tests passing
- ✅ 4 advanced test scenarios passing
- ✅ Manual API testing successful
- ✅ Integration verified
- ✅ Error handling validated

## Documentation

- `TEST_README.md` - Complete test documentation
- `IMPLEMENTATION_SUMMARY.md` - Full implementation details
- `demo_ai_company_size.py` - Working demonstration

## Next Steps

1. Set `OPENAI_API_KEY` to enable AI mode (optional)
2. Run tests to verify installation
3. Test with actual customers via API
4. Monitor lead scoring accuracy

## Support

If you encounter issues:
1. Check `TEST_README.md` troubleshooting section
2. Run `test_lead_scoring_ai.py` to verify setup
3. Review `IMPLEMENTATION_SUMMARY.md` for details

## Cost

With OpenAI API enabled:
- ~10 tokens per request
- ~$0.000015 per lead score
- ~$0.15 per 10,000 leads

Without API (heuristic only): FREE
