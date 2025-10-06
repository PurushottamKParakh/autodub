import hashlib
import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages caching for expensive operations in the dubbing pipeline
    """
    
    def __init__(self, cache_dir='cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[CACHE] Cache directory: {self.cache_dir}")
    
    def get_cache_key(self, data):
        """
        Generate cache key from data
        
        Args:
            data: Dictionary of data to hash
            
        Returns:
            str: MD5 hash of data
        """
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()
    
    def _file_hash(self, file_path):
        """
        Generate hash of file content
        
        Args:
            file_path: Path to file
            
        Returns:
            str: MD5 hash of file content
        """
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    # ==================== TRANSCRIPTION CACHE ====================
    
    def get_cached_transcription(self, audio_path, language, video_url=None, start_time=None, end_time=None):
        """
        Check if transcription is cached
        
        Args:
            audio_path: Path to audio file
            language: Source language code
            video_url: Optional YouTube URL for job-agnostic caching
            start_time: Optional start time for time-range specific caching
            end_time: Optional end time for time-range specific caching
            
        Returns:
            dict or None: Cached transcription or None if not found
        """
        try:
            # Use video URL + time range for cache key if provided (job-agnostic)
            if video_url:
                cache_key = self.get_cache_key({
                    'video_url': video_url,
                    'start_time': start_time,
                    'end_time': end_time,
                    'language': language,
                    'type': 'transcription'
                })
            else:
                # Fallback to audio file hash
                audio_hash = self._file_hash(audio_path)
                cache_key = self.get_cache_key({
                    'audio_hash': audio_hash,
                    'language': language,
                    'type': 'transcription'
                })
            
            cache_file = self.cache_dir / f"transcription_{cache_key}.json"
            
            if cache_file.exists():
                logger.info(f"[CACHE] ✅ Transcription cache HIT: {cache_key[:8]}...")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.info(f"[CACHE] ❌ Transcription cache MISS: {cache_key[:8]}...")
                return None
        except Exception as e:
            logger.warning(f"[CACHE] Failed to read transcription cache: {e}")
            return None
    
    def cache_transcription(self, audio_path, language, transcription, video_url=None, start_time=None, end_time=None):
        """
        Cache transcription result
        
        Args:
            audio_path: Path to audio file
            language: Source language code
            transcription: Transcription result to cache
            video_url: Optional YouTube URL for job-agnostic caching
            start_time: Optional start time for time-range specific caching
            end_time: Optional end time for time-range specific caching
        """
        try:
            # Use video URL + time range for cache key if provided (job-agnostic)
            if video_url:
                cache_key = self.get_cache_key({
                    'video_url': video_url,
                    'start_time': start_time,
                    'end_time': end_time,
                    'language': language,
                    'type': 'transcription'
                })
            else:
                # Fallback to audio file hash
                audio_hash = self._file_hash(audio_path)
                cache_key = self.get_cache_key({
                    'audio_hash': audio_hash,
                    'language': language,
                    'type': 'transcription'
                })
            
            cache_file = self.cache_dir / f"transcription_{cache_key}.json"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(transcription, f, ensure_ascii=False, indent=2)
            
            logger.info(f"[CACHE] 💾 Transcription cached: {cache_key[:8]}...")
        except Exception as e:
            logger.warning(f"[CACHE] Failed to cache transcription: {e}")
    
    # ==================== TRANSLATION CACHE ====================
    
    def get_cached_translation(self, text, source_lang, target_lang):
        """
        Check if translation is cached
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            str or None: Cached translation or None if not found
        """
        try:
            cache_key = self.get_cache_key({
                'text': text,
                'source': source_lang,
                'target': target_lang,
                'type': 'translation'
            })
            cache_file = self.cache_dir / f"translation_{cache_key}.txt"
            
            if cache_file.exists():
                logger.debug(f"[CACHE] ✅ Translation cache HIT: {text[:30]}...")
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.debug(f"[CACHE] ❌ Translation cache MISS: {text[:30]}...")
                return None
        except Exception as e:
            logger.warning(f"[CACHE] Failed to read translation cache: {e}")
            return None
    
    def cache_translation(self, text, source_lang, target_lang, translation):
        """
        Cache translation result
        
        Args:
            text: Original text
            source_lang: Source language code
            target_lang: Target language code
            translation: Translated text
        """
        try:
            cache_key = self.get_cache_key({
                'text': text,
                'source': source_lang,
                'target': target_lang,
                'type': 'translation'
            })
            cache_file = self.cache_dir / f"translation_{cache_key}.txt"
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(translation)
            
            logger.debug(f"[CACHE] 💾 Translation cached: {text[:30]}...")
        except Exception as e:
            logger.warning(f"[CACHE] Failed to cache translation: {e}")
    
    # ==================== VOICE CLONING CACHE ====================
    
    def get_cached_voice(self, audio_path, voice_name, video_url=None, speaker_id=None):
        """
        Check if voice cloning result is cached
        
        Args:
            audio_path: Path to speaker audio sample
            voice_name: Name of the voice
            video_url: Optional YouTube URL for job-agnostic caching
            speaker_id: Optional speaker ID for job-agnostic caching
            
        Returns:
            str or None: Cached voice ID or None if not found
        """
        try:
            # Use video URL + speaker ID for cache key if provided (job-agnostic)
            if video_url and speaker_id is not None:
                cache_key = self.get_cache_key({
                    'video_url': video_url,
                    'speaker_id': speaker_id,
                    'type': 'voice_clone'
                })
                log_name = f"speaker_{speaker_id}"
            else:
                # Fallback to audio file hash + voice name
                audio_hash = self._file_hash(audio_path)
                cache_key = self.get_cache_key({
                    'audio_hash': audio_hash,
                    'voice_name': voice_name,
                    'type': 'voice_clone'
                })
                log_name = voice_name
            
            cache_file = self.cache_dir / f"voice_{cache_key}.txt"
            
            if cache_file.exists():
                logger.info(f"[CACHE] ✅ Voice clone cache HIT: {log_name}")
                with open(cache_file, 'r') as f:
                    return f.read().strip()
            else:
                logger.info(f"[CACHE] ❌ Voice clone cache MISS: {log_name}")
                return None
        except Exception as e:
            logger.warning(f"[CACHE] Failed to read voice cache: {e}")
            return None
    
    def cache_voice(self, audio_path, voice_name, voice_id, video_url=None, speaker_id=None):
        """
        Cache voice cloning result
        
        Args:
            audio_path: Path to speaker audio sample
            voice_name: Name of the voice
            voice_id: ElevenLabs voice ID
            video_url: Optional YouTube URL for job-agnostic caching
            speaker_id: Optional speaker ID for job-agnostic caching
        """
        try:
            # Use video URL + speaker ID for cache key if provided (job-agnostic)
            if video_url and speaker_id is not None:
                cache_key = self.get_cache_key({
                    'video_url': video_url,
                    'speaker_id': speaker_id,
                    'type': 'voice_clone'
                })
                log_name = f"speaker_{speaker_id}"
            else:
                # Fallback to audio file hash + voice name
                audio_hash = self._file_hash(audio_path)
                cache_key = self.get_cache_key({
                    'audio_hash': audio_hash,
                    'voice_name': voice_name,
                    'type': 'voice_clone'
                })
                log_name = voice_name
            
            cache_file = self.cache_dir / f"voice_{cache_key}.txt"
            
            with open(cache_file, 'w') as f:
                f.write(voice_id)
            
            logger.info(f"[CACHE] 💾 Voice clone cached: {log_name} → {voice_id}")
        except Exception as e:
            logger.warning(f"[CACHE] Failed to cache voice: {e}")
    
    # ==================== CACHE MANAGEMENT ====================
    
    def clear_cache(self, cache_type=None):
        """
        Clear cache files
        
        Args:
            cache_type: Type of cache to clear ('transcription', 'translation', 'voice_clone', or None for all)
        """
        try:
            if cache_type:
                pattern = f"{cache_type}_*.json" if cache_type == 'transcription' else f"{cache_type}_*.txt"
                files = list(self.cache_dir.glob(pattern))
            else:
                files = list(self.cache_dir.glob("*"))
            
            for file in files:
                file.unlink()
            
            logger.info(f"[CACHE] Cleared {len(files)} cache files ({cache_type or 'all'})")
        except Exception as e:
            logger.warning(f"[CACHE] Failed to clear cache: {e}")
    
    def get_cache_stats(self):
        """
        Get cache statistics
        
        Returns:
            dict: Cache statistics
        """
        try:
            transcription_files = list(self.cache_dir.glob("transcription_*.json"))
            translation_files = list(self.cache_dir.glob("translation_*.txt"))
            voice_files = list(self.cache_dir.glob("voice_*.txt"))
            
            total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*") if f.is_file())
            
            return {
                'transcriptions': len(transcription_files),
                'translations': len(translation_files),
                'voices': len(voice_files),
                'total_files': len(transcription_files) + len(translation_files) + len(voice_files),
                'total_size_mb': total_size / (1024 * 1024)
            }
        except Exception as e:
            logger.warning(f"[CACHE] Failed to get cache stats: {e}")
            return {}
