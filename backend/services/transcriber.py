from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import os
import logging
from .cache_manager import CacheManager

logger = logging.getLogger(__name__)

class Transcriber:
    """Service for transcribing audio using Deepgram"""
    
    def __init__(self, api_key=None, use_cache=True, video_url=None, start_time=None, end_time=None):
        # CRITICAL: Clear proxy environment variables FIRST
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 
                      'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy']
        for var in proxy_vars:
            if var in os.environ:
                del os.environ[var]
        
        self.api_key = api_key or os.getenv('DEEPGRAM_API_KEY')
        if not self.api_key:
            raise ValueError("Deepgram API key is required")
        
        logger.info(f"[TRANSCRIBER] Initializing Deepgram client...")
        logger.info(f"[TRANSCRIBER] API key found: {self.api_key[:10]}...{self.api_key[-4:]}")
        
        # Initialize client with API key
        try:
            self.client = DeepgramClient(api_key=self.api_key)
            logger.info(f"[TRANSCRIBER] ✅ Deepgram client initialized successfully")
        except Exception as e:
            logger.error(f"[TRANSCRIBER] ❌ Failed to initialize Deepgram client: {e}")
            raise
        
        # Initialize cache with video metadata for job-agnostic caching
        self.use_cache = use_cache
        self.video_url = video_url
        self.start_time = start_time
        self.end_time = end_time
        if self.use_cache:
            self.cache = CacheManager()
            logger.info(f"[TRANSCRIBER] Cache enabled")
    
    def transcribe_audio(self, audio_path, language='en'):
        """
        Transcribe audio file with timestamps
        
        Args:
            audio_path: Path to audio file
            language: Source language code (e.g., 'en', 'es')
            
        Returns:
            dict: Transcription with timestamps
        """
        # Check cache first (with video_url for job-agnostic caching)
        if self.use_cache:
            cached = self.cache.get_cached_transcription(
                audio_path, language, self.video_url, self.start_time, self.end_time
            )
            if cached:
                logger.info(f"[TRANSCRIBER] Using cached transcription")
                return cached
        
        try:
            logger.info(f"[TRANSCRIBER] Reading audio file: {audio_path}")
            
            with open(audio_path, 'rb') as audio_file:
                buffer_data = audio_file.read()
            
            # Create payload
            payload: FileSource = {
                "buffer": buffer_data,
            }
            
            # Configure options with enhanced parameters
            options = PrerecordedOptions(
                model="nova-3",              # Latest and most accurate model
                language=language,            # Source language
                smart_format=True,            # Auto-format numbers, dates, etc.
                punctuate=True,               # Add punctuation
                paragraphs=True,              # Group into paragraphs
                utterances=True,              # Detect natural speech breaks
                diarize=True,                 # Speaker diarization # Latest diarization model
                filler_words=True,            # Include filler words (um, uh)
                numerals=True,                # Convert numbers to numerals
                profanity_filter=False,       # Don't censor profanity
                redact=False,                 # Don't redact PII
                multichannel=False,           # Single audio channel
                alternatives=1,               # Only need best transcription                 # Use nova tier for best quality
            )
            
            logger.info(f"[TRANSCRIBER] Sending transcription request...")
            
            # Call the transcribe_file method
            response = self.client.listen.prerecorded.v("1").transcribe_file(
                payload, 
                options
            )
            
            logger.info(f"[TRANSCRIBER] ✅ Transcription completed")
            
            # Parse the response
            transcription_data = self._parse_transcription(response.to_dict())
            
            # Cache the result (with video_url for job-agnostic caching)
            if self.use_cache:
                self.cache.cache_transcription(
                    audio_path, language, transcription_data,
                    self.video_url, self.start_time, self.end_time
                )
            
            return transcription_data
            
        except Exception as e:
            logger.error(f"[TRANSCRIBER] ❌ Transcription failed: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _parse_transcription(self, response):
        """Parse Deepgram response to extract text, timestamps, and speaker info"""
        try:
            results = response.get('results', {})
            channels = results.get('channels', [])
            
            if not channels:
                return {'segments': [], 'full_text': '', 'speaker_count': 0}
            
            alternatives = channels[0].get('alternatives', [])
            if not alternatives:
                return {'segments': [], 'full_text': '', 'speaker_count': 0}
            
            words = alternatives[0].get('words', [])
            paragraphs = alternatives[0].get('paragraphs', {})
            full_text = alternatives[0].get('transcript', '')
            
            # Extract unique speakers from words
            speakers = set()
            for word in words:
                if 'speaker' in word:
                    speakers.add(word['speaker'])
            
            # Fallback: Check utterances for speaker changes if diarization found only 1 speaker
            if len(speakers) <= 1:
                utterances_data = results.get('utterances', [])
                # Handle both dict and list formats
                if isinstance(utterances_data, dict):
                    utterances = utterances_data.get('utterances', [])
                else:
                    utterances = utterances_data
                
                if utterances:
                    for utterance in utterances:
                        if 'speaker' in utterance:
                            speakers.add(utterance['speaker'])
                    logger.info(f"[TRANSCRIBER] Diarization found {len(speakers)} speaker(s) via utterances fallback")
            
            logger.info(f"[TRANSCRIBER] Detected {len(speakers)} unique speaker(s): {sorted(speakers)}")
            
            segments = []
            if paragraphs and 'paragraphs' in paragraphs:
                segments = self._create_segments_from_paragraphs(paragraphs, words)
            else:
                segments = self._create_segments_from_words(words)
            
            # Fallback: If only 1 speaker detected but we have multiple segments,
            # assume it's a conversation and alternate speakers
            speaker_count = len(speakers)
            if len(speakers) <= 1 and len(segments) > 3:
                logger.info(f"[TRANSCRIBER] Only 1 speaker detected but {len(segments)} segments found")
                logger.info(f"[TRANSCRIBER] Applying conversation heuristic: alternating speakers")
                segments = self._apply_conversation_heuristic(segments)
                speaker_count = 2  # Override to 2 speakers
                logger.info(f"[TRANSCRIBER] Reassigned speakers - now treating as 2-speaker conversation")
            
            result = {
                'full_text': full_text,
                'segments': segments,
                'words': words,
                'speaker_count': speaker_count
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to parse transcription: {str(e)}")
    
    def _apply_conversation_heuristic(self, segments):
        """
        Apply conversation heuristic to assign alternating speakers
        Useful when diarization fails to detect multiple speakers
        
        Args:
            segments: List of segments with speaker info
            
        Returns:
            list: Segments with reassigned speakers
        """
        # Simple alternating pattern for interview/conversation format
        for i, segment in enumerate(segments):
            # Alternate between speaker 0 and 1
            segment['speaker'] = i % 2
        
        return segments
    
    def _create_segments_from_paragraphs(self, paragraphs, words):
        """Create segments from paragraphs with speaker information"""
        segments = []
        
        for para in paragraphs.get('paragraphs', []):
            for sentence in para.get('sentences', []):
                sentence_start = sentence.get('start', 0)
                sentence_end = sentence.get('end', 0)
                sentence_text = sentence.get('text', '')
                
                # Find speaker for this sentence by checking words in time range
                speaker = self._get_speaker_for_timerange(words, sentence_start, sentence_end)
                
                segments.append({
                    'text': sentence_text,
                    'start': sentence_start,
                    'end': sentence_end,
                    'speaker': speaker
                })
        
        return segments
    
    def _get_speaker_for_timerange(self, words, start_time, end_time):
        """Determine the primary speaker for a time range"""
        speaker_counts = {}
        
        for word in words:
            word_start = word.get('start', 0)
            if start_time <= word_start <= end_time:
                speaker = word.get('speaker', 0)
                speaker_counts[speaker] = speaker_counts.get(speaker, 0) + 1
        
        # Return the speaker with the most words in this range
        if speaker_counts:
            return max(speaker_counts, key=speaker_counts.get)
        return 0
    
    def _create_segments_from_words(self, words, max_duration=10):
        """Create segments from words when sentence info is not available"""
        segments = []
        current_segment = {'text': '', 'start': 0, 'end': 0, 'words': [], 'speaker': None}
        
        for word in words:
            word_text = word.get('word', '')
            word_start = word.get('start', 0)
            word_end = word.get('end', 0)
            word_speaker = word.get('speaker', 0)
            
            # Start new segment if speaker changes or duration exceeded
            if current_segment['text']:
                speaker_changed = (current_segment['speaker'] is not None and 
                                 current_segment['speaker'] != word_speaker)
                duration_exceeded = (word_end - current_segment['start'] > max_duration)
                sentence_end = (word_text.endswith('.') or word_text.endswith('?') or word_text.endswith('!'))
                
                if speaker_changed or duration_exceeded or sentence_end:
                    segments.append({
                        'text': current_segment['text'].strip(),
                        'start': current_segment['start'],
                        'end': current_segment['end'],
                        'speaker': current_segment['speaker']
                    })
                    current_segment = {'text': '', 'start': 0, 'end': 0, 'words': [], 'speaker': None}
            
            if not current_segment['text']:
                current_segment['start'] = word_start
                current_segment['speaker'] = word_speaker
            
            current_segment['text'] += word_text + ' '
            current_segment['end'] = word_end
            current_segment['words'].append(word)
        
        if current_segment['text']:
            segments.append({
                'text': current_segment['text'].strip(),
                'start': current_segment['start'],
                'end': current_segment['end'],
                'speaker': current_segment['speaker']
            })
        
        return segments