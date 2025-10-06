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


================================================================================



## Quick Start Guide (from START_HERE.md)

# 🎬 START HERE - Autodub Setup Guide

Welcome to Autodub! This guide will get you up and running in **5 minutes**.

---

## 📋 What You Have

A complete automated video dubbing platform with:
- ✅ Python Flask backend with full dubbing pipeline
- ✅ Modern web frontend with real-time progress tracking
- ✅ Integration with Deepgram, OpenAI, and ElevenLabs
- ✅ Support for 11+ languages
- ✅ Automatic video download, transcription, translation, and synthesis

---

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies

**Install ffmpeg** (required for audio/video processing):
```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get install ffmpeg

# Windows - download from https://ffmpeg.org/download.html
```

**Run the setup script**:
```bash
./setup.sh
```

This will:
- Create virtual environment
- Install Python dependencies
- Create necessary directories
- Generate `.env` file

### Step 2: Configure API Keys

Edit `backend/.env` and add your API keys:

```bash
cd backend
nano .env  # or use your favorite editor
```

Add these keys:
```env
DEEPGRAM_API_KEY=your_deepgram_key_here
OPENAI_API_KEY=your_openai_key_here
ELEVENLABS_API_KEY=sk_bc6473a4d214eb893ecc1bb3d5c7b7ddee9bdb6739b5c786
```

**Where to get API keys:**
- **Deepgram**: https://console.deepgram.com/signup
- **OpenAI**: https://platform.openai.com/api-keys
- **ElevenLabs**: Already provided above ✅

### Step 3: Start the Application

**Terminal 1 - Start Backend:**
```bash
cd backend
source venv/bin/activate
python app.py
```

You should see:
```
* Running on http://0.0.0.0:5000
```

**Terminal 2 - Start Frontend:**
```bash
cd frontend
python -m http.server 8000
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8000
```

**Open your browser:**
```
http://localhost:8000
```

---

## 🎯 Test It Out

1. **Find a short YouTube video** (1-2 minutes recommended for first test)
   - Example: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`

2. **Paste the URL** in the form

3. **Select target language** (e.g., Spanish)

4. **Click "Start Dubbing"**

5. **Watch the progress** - it will show:
   - Downloading video (10-20%)
   - Transcribing audio (20-45%)
   - Translating text (45-60%)
   - Synthesizing speech (60-75%)
   - Aligning audio (75-90%)
   - Merging video (90-100%)

6. **Download your dubbed video!** 🎉

---

## 📚 Documentation

- **Quick Start**: `QUICKSTART.md` - Detailed setup instructions
- **README**: `README.md` - Full documentation
- **Project Overview**: `PROJECT_OVERVIEW.md` - Architecture details
- **Implementation Status**: `IMPLEMENTATION_STATUS.md` - What's built
- **Deployment**: `DEPLOYMENT_CHECKLIST.md` - Production deployment

---

## 🔧 Verify Setup

Run the test script to verify everything is configured:

```bash
cd backend
source venv/bin/activate
python test_setup.py
```

This will check:
- ✅ Python version
- ✅ Dependencies installed
- ✅ ffmpeg available
- ✅ API keys configured
- ✅ Directories created
- ✅ Services importable

---

## 🎨 Supported Languages

- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇮🇹 Italian (it)
- 🇵🇹 Portuguese (pt)
- 🇯🇵 Japanese (ja)
- 🇰🇷 Korean (ko)
- 🇨🇳 Chinese (zh)
- 🇮🇳 Hindi (hi)
- 🇸🇦 Arabic (ar)
- 🇷🇺 Russian (ru)

---

## ⚡ Pro Tips

1. **Start with short videos** (1-2 min) for testing
2. **Monitor the terminal** for detailed logs
3. **Check API quotas** to avoid running out of credits
4. **Use the health check**: `curl http://localhost:5000/health`
5. **Clear temp files** periodically: `rm -rf backend/temp/*`

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Verify virtual environment is activated
which python  # Should show path to venv/bin/python

# Check API keys are set
cat backend/.env
```

### Frontend can't connect
```bash
# Verify backend is running
curl http://localhost:5000/health

# Check browser console for errors (F12)
```

### Job fails
- Check terminal logs for detailed error
- Verify API keys are correct
- Try a different/shorter video
- Check API quotas

---

## 📁 Project Structure

```
Autodub/
├── backend/              # Python Flask API
│   ├── services/        # Core dubbing services
│   ├── app.py          # Main API server
│   ├── job_manager.py  # Async job processing
│   └── requirements.txt
├── frontend/            # Web UI
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── setup.sh            # Setup script
└── START_HERE.md       # This file
```

---

## 🎯 What's Next?

### Immediate
1. ✅ Complete setup above
2. ✅ Test with a short video
3. ✅ Try different languages
4. ✅ Explore the UI

### Future Enhancements
- 🚧 Multi-speaker voice assignment
- 🚧 Voice cloning for original speakers
- 🚧 Background music preservation
- 🚧 Database persistence
- 🚧 User authentication

---

## 💡 How It Works

```
┌─────────────┐
│ YouTube URL │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Download Video  │ (yt-dlp)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract Audio   │ (ffmpeg)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transcribe      │ (Deepgram)
│ with timestamps │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Translate       │ (OpenAI GPT-4)
│ segments        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Synthesize      │ (ElevenLabs)
│ speech          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Align & Merge   │ (ffmpeg)
│ audio + video   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Dubbed Video! 🎉│
└─────────────────┘
```

---

## 🆘 Need Help?

1. **Check the logs** - Terminal shows detailed progress
2. **Run test script** - `python test_setup.py`
3. **Review docs** - Check README.md and QUICKSTART.md
4. **API issues** - Verify keys and check quotas
5. **File issues** - Check permissions and disk space

---

## 🎉 You're Ready!

Everything is set up and ready to go. Just:

1. **Configure your API keys** in `backend/.env`
2. **Start the servers** (backend + frontend)
3. **Open http://localhost:8000**
4. **Start dubbing videos!**

**Happy dubbing! 🎬✨**

---

*Built for the Autodub Hackathon | Powered by Deepgram, OpenAI & ElevenLabs*


