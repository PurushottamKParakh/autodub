# 🚀 Quick Start Guide

Get Autodub up and running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.8+)
python3 --version

# Check ffmpeg
ffmpeg -version
```

If missing, install:
- **Python**: https://www.python.org/downloads/
- **ffmpeg**: 
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt-get install ffmpeg`

## Automated Setup

```bash
# Run the setup script
./setup.sh
```

## Manual Setup

### 1. Backend Setup

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
nano .env  # Edit and add your API keys
```

### 2. Add API Keys to `.env`

```env
DEEPGRAM_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=sk_bc6473a4d214eb893ecc1bb3d5c7b7ddee9bdb6739b5c786
```

### 3. Start Backend

```bash
# From backend directory with venv activated
python app.py
```

Backend will start on `http://localhost:5000`

### 4. Start Frontend

Open a new terminal:

```bash
cd frontend
python -m http.server 8000
```

Frontend will be available at `http://localhost:8000`

## Test the Application

1. Open browser to `http://localhost:8000`
2. Paste a YouTube URL (try a short video first)
3. Select target language (e.g., Spanish)
4. Click "Start Dubbing"
5. Wait for processing (progress bar will update)
6. Watch/download the dubbed video!

## Test YouTube URLs

Try these short videos for testing:

- **English to Spanish**: https://www.youtube.com/watch?v=dQw4w9WgXcQ
- **Short tech video**: https://www.youtube.com/watch?v=9bZkp7q19f0

## Troubleshooting

### Backend won't start
- Check if all API keys are set in `.env`
- Ensure virtual environment is activated
- Check if port 5000 is available

### Frontend can't connect to backend
- Ensure backend is running on port 5000
- Check browser console for CORS errors
- Try accessing `http://localhost:5000/health` directly

### Video download fails
- Check YouTube URL is valid and accessible
- Some videos may be restricted by region or copyright
- Try a different, shorter video

### Transcription/Translation fails
- Verify API keys are correct
- Check API quotas/limits
- Review backend logs for detailed errors

## API Testing with curl

```bash
# Health check
curl http://localhost:5000/health

# Create dubbing job
curl -X POST http://localhost:5000/api/dub \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "target_language": "es"
  }'

# Check job status (replace JOB_ID)
curl http://localhost:5000/api/dub/JOB_ID

# List all jobs
curl http://localhost:5000/api/jobs
```

## Development Tips

### Watch Backend Logs
The Flask server runs in debug mode by default and will show detailed logs.

### Clear Temporary Files
```bash
cd backend
rm -rf temp/* outputs/*
```

### Restart Services
```bash
# Stop with Ctrl+C, then restart
python app.py  # Backend
python -m http.server 8000  # Frontend
```

## Next Steps

- Try different languages
- Test with longer videos
- Experiment with different content types
- Check the main README.md for advanced features

## Support

If you encounter issues:
1. Check the logs in the terminal
2. Verify all dependencies are installed
3. Ensure API keys are valid
4. Try with a simpler/shorter video first

Happy dubbing! 🎬✨
