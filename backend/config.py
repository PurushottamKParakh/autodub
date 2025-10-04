import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True') == 'True'
    PORT = int(os.getenv('PORT', 5000))
    
    # API Keys
    DEEPGRAM_API_KEY = os.getenv('DEEPGRAM_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    
    # Directories
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'outputs')
    TEMP_FOLDER = os.getenv('TEMP_FOLDER', 'temp')
    
    # File size limits
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB
    
    # Language settings
    DEFAULT_SOURCE_LANGUAGE = 'en'
    DEFAULT_TARGET_LANGUAGE = 'es'
    
    SUPPORTED_LANGUAGES = {
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'hi': 'Hindi',
        'ar': 'Arabic',
        'ru': 'Russian'
    }
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        errors = []
        
        if not Config.DEEPGRAM_API_KEY:
            errors.append("DEEPGRAM_API_KEY is not set")
        
        if not Config.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set")
        
        if not Config.ELEVENLABS_API_KEY:
            errors.append("ELEVENLABS_API_KEY is not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
