#!/bin/bash

echo "🎬 Autodub Setup Script"
echo "======================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg is not installed."
    echo "Please install ffmpeg:"
    echo "  macOS: brew install ffmpeg"
    echo "  Linux: sudo apt-get install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

echo "✅ ffmpeg found: $(ffmpeg -version | head -n 1)"
echo ""

# Setup backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit backend/.env and add your API keys:"
    echo "   - DEEPGRAM_API_KEY"
    echo "   - OPENAI_API_KEY"
    echo "   - ELEVENLABS_API_KEY (already provided)"
    echo ""
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p uploads outputs temp

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit backend/.env and add your API keys"
echo "2. Start the backend: cd backend && source venv/bin/activate && python app.py"
echo "3. Start the frontend: cd frontend && python -m http.server 8000"
echo "4. Open http://localhost:8000 in your browser"
echo ""
