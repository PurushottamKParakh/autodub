import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist"""
    directories = ['uploads', 'outputs', 'temp']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {directory}")

def cleanup_old_files(directory, max_age_hours=24):
    """
    Clean up files older than specified hours
    
    Args:
        directory: Directory to clean
        max_age_hours: Maximum age of files in hours
    """
    import time
    
    if not os.path.exists(directory):
        return
    
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            
            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    logger.info(f"Cleaned up old file: {filepath}")
                except Exception as e:
                    logger.error(f"Failed to delete {filepath}: {e}")

def get_file_size_mb(filepath):
    """
    Get file size in megabytes
    
    Args:
        filepath: Path to file
        
    Returns:
        float: File size in MB
    """
    if not os.path.exists(filepath):
        return 0
    
    size_bytes = os.path.getsize(filepath)
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)

def format_duration(seconds):
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        str: Formatted duration (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{int(seconds)}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"
    
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    
    return f"{hours}h {remaining_minutes}m {remaining_seconds}s"

def validate_youtube_url(url):
    """
    Validate if URL is a valid YouTube URL
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid YouTube URL
    """
    youtube_patterns = [
        'youtube.com/watch?v=',
        'youtu.be/',
        'youtube.com/embed/',
        'youtube.com/v/'
    ]
    
    return any(pattern in url for pattern in youtube_patterns)

def get_storage_info():
    """
    Get storage information for temp and output directories
    
    Returns:
        dict: Storage information
    """
    info = {
        'temp': {
            'files': 0,
            'size_mb': 0
        },
        'outputs': {
            'files': 0,
            'size_mb': 0
        }
    }
    
    for directory in ['temp', 'outputs']:
        if os.path.exists(directory):
            files = os.listdir(directory)
            info[directory]['files'] = len(files)
            
            total_size = 0
            for filename in files:
                filepath = os.path.join(directory, filename)
                if os.path.isfile(filepath):
                    total_size += os.path.getsize(filepath)
            
            info[directory]['size_mb'] = round(total_size / (1024 * 1024), 2)
    
    return info

def safe_filename(filename):
    """
    Convert filename to safe version (remove special characters)
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    import re
    
    # Remove special characters, keep alphanumeric, dots, dashes, underscores
    safe = re.sub(r'[^\w\s\-\.]', '', filename)
    
    # Replace spaces with underscores
    safe = safe.replace(' ', '_')
    
    # Remove multiple consecutive underscores
    safe = re.sub(r'_+', '_', safe)
    
    return safe

class ProgressTracker:
    """Track progress of multi-step operations"""
    
    def __init__(self, total_steps):
        self.total_steps = total_steps
        self.current_step = 0
        self.step_weights = [100 / total_steps] * total_steps
    
    def set_step_weights(self, weights):
        """
        Set custom weights for each step
        
        Args:
            weights: List of weights (should sum to 100)
        """
        if len(weights) != self.total_steps:
            raise ValueError("Number of weights must match total steps")
        
        if sum(weights) != 100:
            raise ValueError("Weights must sum to 100")
        
        self.step_weights = weights
    
    def get_progress(self, step_index, step_progress=0):
        """
        Get overall progress percentage
        
        Args:
            step_index: Current step index (0-based)
            step_progress: Progress within current step (0-100)
            
        Returns:
            int: Overall progress (0-100)
        """
        # Progress from completed steps
        completed_progress = sum(self.step_weights[:step_index])
        
        # Progress from current step
        current_step_progress = (self.step_weights[step_index] * step_progress) / 100
        
        total_progress = completed_progress + current_step_progress
        
        return int(min(100, max(0, total_progress)))
