# Logging Guide

## Overview
Comprehensive logging has been added to the autodub backend to help diagnose API errors and track the dubbing pipeline progress.

## What Was Added

### 1. Application-Wide Logging Configuration
**File:** `backend/app.py`
- Configured Python's logging module with INFO level
- Format: `YYYY-MM-DD HH:MM:SS [LEVEL] module_name: message`
- All logs appear in the server console output

### 2. Synthesizer Detailed Error Logging
**File:** `backend/services/synthesizer.py`

**Logs include:**
- Text being synthesized (first 50 chars)
- Voice ID and model being used
- Success confirmation with audio byte count
- **Detailed error information:**
  - Error type (e.g., `RateLimitError`, `QuotaExceededError`)
  - Full error message
  - Exception representation
  - **Automatic detection of:**
    - Rate limit errors (keywords: "rate", "limit")
    - Quota exceeded errors (keyword: "quota")
    - Authentication errors (keywords: "auth", "key")

### 3. Pipeline Error Logging
**File:** `backend/services/pipeline.py`

**Logs include:**
- Job ID that failed
- Error type
- Error message
- Full exception details

## How to Use

### Reading Logs

When you run the backend server, you'll now see detailed logs like:

```
2025-10-05 00:30:15 [INFO] services.synthesizer: [SYNTHESIZER] Generating speech for text: Hello, this is a test...
2025-10-05 00:30:15 [INFO] services.synthesizer: [SYNTHESIZER] Using voice_id: 21m00Tcm4TlvDq8ikWAM, model: eleven_multilingual_v2
2025-10-05 00:30:16 [INFO] services.synthesizer: [SYNTHESIZER] Successfully generated 45678 bytes of audio
```

### Error Detection

When an error occurs, you'll see:

```
2025-10-05 00:30:20 [ERROR] services.synthesizer: [SYNTHESIZER ERROR] Type: RateLimitError
2025-10-05 00:30:20 [ERROR] services.synthesizer: [SYNTHESIZER ERROR] Message: Rate limit exceeded. Please try again later.
2025-10-05 00:30:20 [ERROR] services.synthesizer: [SYNTHESIZER ERROR] Full exception: RateLimitError('Rate limit exceeded')
2025-10-05 00:30:20 [ERROR] services.synthesizer: [SYNTHESIZER ERROR] RATE LIMIT DETECTED - ElevenLabs API quota exceeded
```

### Specific Error Types Detected

1. **Rate Limit Errors**
   - Keywords: "rate", "limit"
   - Message: `RATE LIMIT DETECTED - ElevenLabs API quota exceeded`

2. **Quota Exceeded**
   - Keyword: "quota"
   - Message: `QUOTA EXCEEDED - ElevenLabs character limit reached`

3. **Authentication Errors**
   - Keywords: "auth", "key"
   - Message: `AUTHENTICATION ERROR - Invalid API key`

## Testing the Logging

1. Start the backend server:
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. Create a dubbing job from the frontend

3. Watch the console output for detailed logs

4. If an error occurs, you'll see:
   - Exact error type
   - Full error message
   - Automatic categorization of the error

## Benefits

✅ **No more guessing** - Exact error types and messages are logged
✅ **Easy debugging** - See which step failed and why
✅ **API limit tracking** - Know when you hit rate limits or quotas
✅ **Better monitoring** - Track progress through the pipeline

## Next Steps

If you encounter errors:
1. Check the console logs for the error type
2. Look for the `[SYNTHESIZER ERROR]` or `[PIPELINE ERROR]` tags
3. The logs will tell you exactly which limit was crossed
4. Take appropriate action based on the error type
