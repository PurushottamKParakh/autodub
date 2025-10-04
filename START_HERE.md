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
