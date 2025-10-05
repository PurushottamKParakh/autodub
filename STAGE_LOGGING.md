# Stage-by-Stage Logging Guide

## Overview
The backend now displays detailed, stage-by-stage progress logs for every dubbing job in the console/terminal.

## What You'll See

When you run a dubbing job, the console will show:

### Stage 1: Downloading Video
```
================================================================================
[STAGE 1/6] DOWNLOADING VIDEO
================================================================================
Job ID: abc123-def456-...
YouTube URL: https://www.youtube.com/watch?v=...
Target Language: es
Source Language: en

✅ STAGE 1 COMPLETE: Video downloaded successfully
   Video Path: temp/abc123_video.mp4
   Video Title: Sample Video Title
```

### Stage 2: Extracting Audio
```
================================================================================
[STAGE 2/6] EXTRACTING AUDIO
================================================================================

✅ STAGE 2 COMPLETE: Audio extracted successfully
   Audio Path: temp/abc123_original_audio.wav
```

### Stage 3: Transcribing Audio
```
================================================================================
[STAGE 3/6] TRANSCRIBING AUDIO
================================================================================
Language: en

✅ STAGE 3 COMPLETE: Transcription successful
   Segments: 15
   Full Text Preview: Hello, this is a sample video about automated dubbing...
```

### Stage 4: Translating Text
```
================================================================================
[STAGE 4/6] TRANSLATING TEXT
================================================================================
From: en → To: es
Segments to translate: 15

✅ STAGE 4 COMPLETE: Translation successful
   Translated Segments: 15
   Sample Translation: 'Hello, this is a sample video' → 'Hola, este es un video de muestra'
```

### Stage 5: Synthesizing Speech
```
================================================================================
[STAGE 5/6] SYNTHESIZING SPEECH
================================================================================
Voice ID: 21m00Tcm4TlvDq8ikWAM
Segments to synthesize: 15

✅ STAGE 5 COMPLETE: Speech synthesis successful
   Synthesized Segments: 15
   Segments with audio: 15/15
```

### Stage 6: Aligning & Merging
```
================================================================================
[STAGE 6/6] ALIGNING & MERGING AUDIO
================================================================================

✅ Audio alignment complete
   Dubbed Audio Path: temp/abc123_dubbed_audio.mp3

📹 Merging dubbed audio with original video...

✅ STAGE 6 COMPLETE: Video merging successful
   Output Video: outputs/abc123_dubbed.mp4
```

### Final Summary
```
================================================================================
🎉 DUBBING PIPELINE COMPLETE!
================================================================================
Job ID: abc123-def456-...
Output File: outputs/abc123_dubbed.mp4
Total Segments: 15
================================================================================
```

## Error Logging

If any stage fails, you'll see detailed error information:

```
[PIPELINE ERROR] Job abc123 failed
[PIPELINE ERROR] Type: RateLimitError
[PIPELINE ERROR] Message: Rate limit exceeded
[PIPELINE ERROR] Full exception: RateLimitError('...')
```

## Benefits

✅ **Clear Progress Tracking** - See exactly which stage is running
✅ **Detailed Information** - View paths, counts, and sample data
✅ **Easy Debugging** - Know immediately where failures occur
✅ **Professional Output** - Clean, formatted console logs

## How to View

Simply run your backend server and watch the console:

```bash
cd backend
source venv/bin/activate
python app.py
```

Then create a dubbing job and watch the detailed stage-by-stage progress in real-time!
