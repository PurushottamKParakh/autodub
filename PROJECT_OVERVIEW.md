# 🎬 Autodub - Project Overview

## Executive Summary

Autodub is a complete automated video dubbing pipeline built for the Autodub Hackathon. It transforms YouTube videos from one language to another while maintaining timing, synchronization, and audio quality.

## Architecture

### High-Level Flow

```
YouTube URL → Download → Extract Audio → Transcribe → Translate → Synthesize → Align → Merge → Dubbed Video
```

### Technology Stack

**Backend (Python)**
- Flask - REST API framework
- yt-dlp - YouTube video downloader
- Deepgram - Speech-to-text with timestamps
- OpenAI GPT-4 - Translation
- ElevenLabs - Text-to-speech synthesis
- ffmpeg - Audio/video processing

**Frontend (Vanilla JS)**
- HTML5/CSS3 - Modern, responsive UI
- JavaScript - API integration and real-time updates
- No framework dependencies

## Project Structure

```
Autodub/
├── backend/
│   ├── services/              # Core dubbing services
│   │   ├── downloader.py      # YouTube download (yt-dlp)
│   │   ├── transcriber.py     # Speech-to-text (Deepgram)
│   │   ├── translator.py      # Translation (OpenAI)
│   │   ├── synthesizer.py     # Text-to-speech (ElevenLabs)
│   │   ├── audio_processor.py # Audio manipulation (ffmpeg)
│   │   └── pipeline.py        # Orchestration
│   ├── app.py                 # Flask API server
│   ├── job_manager.py         # Async job processing
│   ├── config.py              # Configuration
│   ├── utils.py               # Utility functions
│   ├── test_setup.py          # Setup verification
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── index.html             # Main UI
│   ├── styles.css             # Styling
│   └── app.js                 # Frontend logic
├── setup.sh                   # Automated setup script
├── README.md                  # Full documentation
├── QUICKSTART.md              # Quick start guide
└── PROJECT_OVERVIEW.md        # This file
```

## Core Components

### 1. Video Downloader (`services/downloader.py`)
- Downloads YouTube videos using yt-dlp
- Extracts audio in WAV format
- Handles various video formats and qualities

### 2. Transcriber (`services/transcriber.py`)
- Uses Deepgram for accurate transcription
- Provides word-level and sentence-level timestamps
- Supports speaker diarization for multi-speaker content
- Segments audio into manageable chunks

### 3. Translator (`services/translator.py`)
- Translates text using OpenAI GPT-4
- Maintains context and tone
- Batch processing for efficiency
- Supports 11+ languages

### 4. Speech Synthesizer (`services/synthesizer.py`)
- Generates natural-sounding speech with ElevenLabs
- Multilingual voice support
- High-quality audio output
- Per-segment synthesis for timing control

### 5. Audio Processor (`services/audio_processor.py`)
- Extracts audio from video (ffmpeg)
- Adjusts audio speed while preserving pitch
- Concatenates segments with proper timing
- Merges dubbed audio with original video

### 6. Pipeline Orchestrator (`services/pipeline.py`)
- Coordinates all services
- Manages workflow: Download → Transcribe → Translate → Synthesize → Merge
- Real-time progress tracking
- Error handling and recovery

### 7. Job Manager (`job_manager.py`)
- Async job processing with threading
- Job status tracking
- Thread-safe operations
- Progress updates

### 8. Flask API (`app.py`)
- RESTful endpoints
- CORS support for frontend
- File serving for downloads
- Health checks

## API Endpoints

### `GET /health`
Health check endpoint

### `POST /api/dub`
Create new dubbing job
```json
{
  "youtube_url": "https://youtube.com/watch?v=...",
  "target_language": "es",
  "source_language": "en"
}
```

### `GET /api/dub/{job_id}`
Get job status and progress

### `GET /api/download/{job_id}`
Download completed video

### `GET /api/jobs`
List all jobs

## Pipeline Steps in Detail

### Step 1: Download (10-20%)
- Download video from YouTube
- Extract audio track
- Store temporarily

### Step 2: Transcribe (20-30%)
- Send audio to Deepgram
- Receive timestamped transcription
- Segment into sentences/phrases

### Step 3: Translate (30-45%)
- Translate each segment
- Preserve timing information
- Maintain context across segments

### Step 4: Synthesize (45-75%)
- Generate speech for each segment
- Use appropriate voice for language
- Save individual audio files

### Step 5: Align (75-90%)
- Calculate timing differences
- Adjust speech speed if needed
- Add silence/gaps as required
- Concatenate all segments

### Step 6: Merge (90-100%)
- Replace original audio with dubbed audio
- Ensure video-audio sync
- Export final video

## Key Features

✅ **Implemented**
- Complete dubbing pipeline
- 11+ language support
- Real-time progress tracking
- Modern, responsive UI
- Async job processing
- Automatic cleanup
- Error handling

🚧 **Future Enhancements**
- Multi-speaker voice assignment
- Voice cloning for original speakers
- Background music preservation (demucs)
- Database persistence (Redis/PostgreSQL)
- Queue management (Celery)
- User authentication
- Video preview before download
- Batch processing

## Supported Languages

- Spanish (es)
- French (fr)
- German (de)
- Italian (it)
- Portuguese (pt)
- Japanese (ja)
- Korean (ko)
- Chinese (zh)
- Hindi (hi)
- Arabic (ar)
- Russian (ru)

## Performance Considerations

### Processing Time
- **Short video (1-2 min)**: ~2-5 minutes
- **Medium video (5-10 min)**: ~10-20 minutes
- **Long video (20+ min)**: ~30-60 minutes

Factors affecting speed:
- Video length
- Number of speakers
- Language complexity
- API response times
- Network speed

### Resource Usage
- **CPU**: Moderate (ffmpeg processing)
- **Memory**: ~500MB-2GB depending on video size
- **Disk**: ~3x video size (original + temp + output)
- **Network**: Download + API calls

## Error Handling

The system handles various error scenarios:
- Invalid YouTube URLs
- Download failures
- API rate limits
- Transcription errors
- Translation failures
- Audio processing errors
- Disk space issues

## Security Considerations

- API keys stored in `.env` (not in code)
- `.env` excluded from git
- Input validation on URLs
- File size limits (500MB)
- Temporary file cleanup
- CORS configuration

## Testing Strategy

1. **Setup Verification**: `python test_setup.py`
2. **API Testing**: Use curl or Postman
3. **Integration Testing**: Test with short videos first
4. **Language Testing**: Verify each language pair
5. **Error Testing**: Test with invalid inputs

## Deployment Considerations

### Local Development
- Use provided setup scripts
- Run Flask in debug mode
- Serve frontend with Python HTTP server

### Production (Future)
- Use production WSGI server (Gunicorn)
- Add reverse proxy (Nginx)
- Implement proper logging
- Add monitoring (Prometheus/Grafana)
- Use Redis for job queue
- Add database for persistence
- Implement rate limiting
- Add authentication

## Known Limitations

1. **Timing Accuracy**: Speed adjustment has limits (0.5x-2.0x)
2. **Voice Quality**: Single voice per language (no speaker matching)
3. **Background Audio**: Music/effects are removed
4. **Video Length**: Very long videos may timeout
5. **API Costs**: Each job consumes API credits
6. **Concurrent Jobs**: Limited by threading (no queue system)

## Troubleshooting

### Common Issues

**"Job failed: Transcription failed"**
- Check Deepgram API key
- Verify audio extraction worked
- Check API quota

**"Speed adjustment failed"**
- Translation may be too long/short
- Try shorter video segments
- Check ffmpeg installation

**"Cannot connect to API"**
- Ensure backend is running
- Check port 5000 is available
- Verify CORS settings

## Development Workflow

1. **Setup**: Run `./setup.sh`
2. **Configure**: Edit `.env` with API keys
3. **Test**: Run `python test_setup.py`
4. **Develop**: Make changes to services
5. **Test**: Use short videos for testing
6. **Debug**: Check terminal logs
7. **Iterate**: Refine and improve

## Contributing

This is a hackathon project, but improvements welcome:
- Better error handling
- UI enhancements
- Performance optimizations
- Additional language support
- Voice cloning integration
- Background music preservation

## Credits

**APIs & Tools**
- Deepgram - Transcription
- OpenAI - Translation
- ElevenLabs - Speech synthesis
- yt-dlp - Video download
- ffmpeg - Audio/video processing

**Built for**: Autodub Hackathon
**Framework**: Flask + Vanilla JavaScript
**License**: Hackathon Project

---

**Last Updated**: 2025-10-04
**Version**: 1.0.0
**Status**: MVP Complete ✅
