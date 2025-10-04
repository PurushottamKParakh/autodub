# 🎬 Autodub - AI-Powered Video Dubbing Platform

An automated video dubbing pipeline that transforms YouTube videos from one language to another while maintaining timing and synchronization.

## 🎯 Overview

Autodub is a full-stack application that:
- Downloads YouTube videos
- Transcribes audio with timestamps using Deepgram
- Translates transcriptions using OpenAI GPT-4
- Synthesizes speech in target language using ElevenLabs
- Aligns and merges dubbed audio with original video

## 🏗️ Project Structure

```
Autodub/
├── backend/                 # Python Flask backend
│   ├── venv/               # Virtual environment
│   ├── services/           # Core dubbing services
│   │   ├── downloader.py   # YouTube video downloader
│   │   ├── transcriber.py  # Audio transcription
│   │   ├── translator.py   # Text translation
│   │   ├── synthesizer.py  # Speech synthesis
│   │   └── audio_processor.py  # Audio alignment & merging
│   ├── uploads/            # Temporary uploads
│   ├── outputs/            # Final dubbed videos
│   ├── temp/               # Temporary processing files
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── .gitignore
├── frontend/               # Frontend web interface
│   ├── index.html          # Main HTML page
│   ├── styles.css          # Styling
│   └── app.js              # JavaScript logic
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- ffmpeg (for audio/video processing)
- Node.js (optional, for serving frontend)

### Install ffmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Activate virtual environment:**
```bash
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
DEEPGRAM_API_KEY=your_deepgram_api_key
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=sk_bc6473a4d214eb893ecc1bb3d5c7b7ddee9bdb6739b5c786
```

5. **Run the Flask server:**
```bash
python app.py
```

The backend will start on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Serve the frontend:**

**Option 1: Using Python:**
```bash
python -m http.server 8000
```

**Option 2: Using Node.js:**
```bash
npx serve
```

**Option 3: Open directly:**
Simply open `index.html` in your browser (may have CORS issues)

3. **Access the application:**
Open your browser and go to `http://localhost:8000`

## 📋 API Endpoints

### Health Check
```
GET /health
```
Returns API health status

### Create Dubbing Job
```
POST /api/dub
Content-Type: application/json

{
  "youtube_url": "https://www.youtube.com/watch?v=...",
  "target_language": "es"
}
```

Response:
```json
{
  "job_id": "abc-123-def",
  "status": "queued",
  "message": "Dubbing job created successfully"
}
```

### Get Job Status
```
GET /api/dub/{job_id}
```

Response:
```json
{
  "job_id": "abc-123-def",
  "status": "completed",
  "progress": 100,
  "message": "Dubbing completed",
  "video_url": "/api/download/abc-123-def"
}
```

### Download Video
```
GET /api/download/{job_id}
```
Downloads the dubbed video file

### List All Jobs
```
GET /api/jobs
```

## 🎨 Supported Languages

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

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **yt-dlp** - YouTube video downloader
- **Deepgram** - Speech-to-text transcription
- **OpenAI GPT-4** - Translation
- **ElevenLabs** - Text-to-speech synthesis
- **ffmpeg** - Audio/video processing

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling with modern gradients
- **Vanilla JavaScript** - Logic and API integration

## 📝 Development Notes

### Current Implementation Status

✅ **Completed:**
- Project structure setup
- Backend API endpoints
- Service modules (downloader, transcriber, translator, synthesizer, audio processor)
- Frontend UI with modern design
- Job status tracking
- Multi-language support

⏳ **To Implement:**
- Async job processing (currently synchronous)
- Pipeline orchestration (connecting all services)
- Error handling and retry logic
- File cleanup after processing
- Multi-speaker support
- Voice cloning
- Background music preservation

### Next Steps

1. **Implement Pipeline Orchestrator:**
   - Create `services/pipeline.py` to orchestrate the entire dubbing process
   - Integrate all services (download → transcribe → translate → synthesize → merge)

2. **Add Async Processing:**
   - Use Celery or Python threading for background jobs
   - Update job status in real-time

3. **Enhance Audio Alignment:**
   - Implement speed adjustment for better timing
   - Add silence padding between segments

4. **Testing:**
   - Test with various YouTube videos
   - Validate different languages
   - Check audio-video synchronization

## 🔑 API Keys

### ElevenLabs
- **Email:** support@deeptune.com
- **Password:** happyrobot17!
- **API Key:** sk_bc6473a4d214eb893ecc1bb3d5c7b7ddee9bdb6739b5c786

### Deepgram & OpenAI
You'll need to obtain your own API keys:
- Deepgram: https://deepgram.com
- OpenAI: https://platform.openai.com

## 🐛 Troubleshooting

**Issue: Cannot connect to backend**
- Ensure Flask server is running on port 5000
- Check CORS settings if accessing from different origin

**Issue: ffmpeg not found**
- Install ffmpeg using package manager
- Ensure ffmpeg is in system PATH

**Issue: API key errors**
- Verify all API keys are correctly set in `.env`
- Check API key permissions and quotas

## 📄 License

This project is created for the Autodub Hackathon.

## 🤝 Contributing

This is a hackathon project. Feel free to fork and improve!

---

**Built with ❤️ for the Autodub Hackathon**
