#!/usr/bin/env python3
"""
Test script to verify Autodub setup
"""

import os
import sys
from pathlib import Path

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print("\nChecking Python dependencies...")
    
    required_packages = [
        'flask',
        'flask_cors',
        'yt_dlp',
        'openai',
        'deepgram',
        'elevenlabs',
        'dotenv',
        'requests'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    print("\nChecking ffmpeg...")
    
    import subprocess
    
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"✅ {version_line}")
            return True
        else:
            print("❌ ffmpeg not working properly")
            return False
    except FileNotFoundError:
        print("❌ ffmpeg not found")
        print("   Install: brew install ffmpeg (macOS) or apt-get install ffmpeg (Linux)")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    print("\nChecking environment configuration...")
    
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Run: cp .env.example .env")
        return False
    
    print("✅ .env file exists")
    
    # Load and check keys
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = [
        'DEEPGRAM_API_KEY',
        'OPENAI_API_KEY',
        'ELEVENLABS_API_KEY'
    ]
    
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if value and value != f'your_{key.lower()}_here':
            print(f"✅ {key} is set")
        else:
            print(f"⚠️  {key} not set or using placeholder")
            missing_keys.append(key)
    
    return len(missing_keys) == 0

def check_directories():
    """Check if required directories exist"""
    print("\nChecking directories...")
    
    required_dirs = ['uploads', 'outputs', 'temp', 'services']
    
    all_exist = True
    
    for directory in required_dirs:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ (will be created)")
            dir_path.mkdir(parents=True, exist_ok=True)
            all_exist = False
    
    return True  # Always return True since we create them

def check_services():
    """Check if service modules exist"""
    print("\nChecking service modules...")
    
    services = [
        'services/__init__.py',
        'services/downloader.py',
        'services/transcriber.py',
        'services/translator.py',
        'services/synthesizer.py',
        'services/audio_processor.py',
        'services/pipeline.py'
    ]
    
    all_exist = True
    
    for service in services:
        service_path = Path(service)
        if service_path.exists():
            print(f"✅ {service}")
        else:
            print(f"❌ {service}")
            all_exist = False
    
    return all_exist

def test_imports():
    """Test if services can be imported"""
    print("\nTesting service imports...")
    
    try:
        from services.downloader import VideoDownloader
        print("✅ VideoDownloader")
    except Exception as e:
        print(f"❌ VideoDownloader: {e}")
        return False
    
    try:
        from services.transcriber import Transcriber
        print("✅ Transcriber")
    except Exception as e:
        print(f"❌ Transcriber: {e}")
        return False
    
    try:
        from services.translator import Translator
        print("✅ Translator")
    except Exception as e:
        print(f"❌ Translator: {e}")
        return False
    
    try:
        from services.synthesizer import SpeechSynthesizer
        print("✅ SpeechSynthesizer")
    except Exception as e:
        print(f"❌ SpeechSynthesizer: {e}")
        return False
    
    try:
        from services.audio_processor import AudioProcessor
        print("✅ AudioProcessor")
    except Exception as e:
        print(f"❌ AudioProcessor: {e}")
        return False
    
    try:
        from services.pipeline import DubbingPipeline
        print("✅ DubbingPipeline")
    except Exception as e:
        print(f"❌ DubbingPipeline: {e}")
        return False
    
    return True

def main():
    """Run all checks"""
    print_header("Autodub Setup Verification")
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'ffmpeg': check_ffmpeg(),
        'Environment': check_env_file(),
        'Directories': check_directories(),
        'Service Files': check_services(),
        'Service Imports': test_imports()
    }
    
    print_header("Summary")
    
    all_passed = True
    
    for check, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All checks passed! You're ready to run Autodub.")
        print("\nNext steps:")
        print("1. Make sure your API keys are set in .env")
        print("2. Start the backend: python app.py")
        print("3. Start the frontend: cd ../frontend && python -m http.server 8000")
        print("4. Open http://localhost:8000 in your browser")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Install ffmpeg: brew install ffmpeg (macOS)")
        print("- Create .env file: cp .env.example .env")
        print("- Add your API keys to .env")
    
    print()

if __name__ == '__main__':
    main()
