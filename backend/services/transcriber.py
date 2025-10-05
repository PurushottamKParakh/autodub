from deepgram import DeepgramClient, PrerecordedOptions, FileSource
import os
import logging

logger = logging.getLogger(__name__)

class Transcriber:
    """Service for transcribing audio using Deepgram"""
    
    def __init__(self, api_key=None):
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
    
    def transcribe_audio(self, audio_path, language='en'):
        """
        Transcribe audio file with timestamps
        
        Args:
            audio_path: Path to audio file
            language: Source language code (e.g., 'en', 'es')
            
        Returns:
            dict: Transcription with timestamps
        """
        try:
            logger.info(f"[TRANSCRIBER] Reading audio file: {audio_path}")
            
            with open(audio_path, 'rb') as audio_file:
                buffer_data = audio_file.read()
            
            # Create payload
            payload: FileSource = {
                "buffer": buffer_data,
            }
            
            # Configure options
            options = PrerecordedOptions(
                model="nova-2",
                language=language,
                smart_format=True,
                punctuate=True,
                paragraphs=True,
                utterances=True,
                diarize=True
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
            
            return transcription_data
            
        except Exception as e:
            logger.error(f"[TRANSCRIBER] ❌ Transcription failed: {str(e)}")
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _parse_transcription(self, response):
        """Parse Deepgram response to extract text and timestamps"""
        try:
            results = response.get('results', {})
            channels = results.get('channels', [])
            
            if not channels:
                return {'segments': [], 'full_text': ''}
            
            alternatives = channels[0].get('alternatives', [])
            if not alternatives:
                return {'segments': [], 'full_text': ''}
            
            words = alternatives[0].get('words', [])
            paragraphs = alternatives[0].get('paragraphs', {})
            full_text = alternatives[0].get('transcript', '')
            
            segments = []
            if paragraphs and 'paragraphs' in paragraphs:
                for para in paragraphs['paragraphs']:
                    for sentence in para.get('sentences', []):
                        segments.append({
                            'text': sentence.get('text', ''),
                            'start': sentence.get('start', 0),
                            'end': sentence.get('end', 0)
                        })
            else:
                segments = self._create_segments_from_words(words)
            
            return {
                'full_text': full_text,
                'segments': segments,
                'words': words
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse transcription: {str(e)}")
    
    def _create_segments_from_words(self, words, max_duration=10):
        """Create segments from words when sentence info is not available"""
        segments = []
        current_segment = {'text': '', 'start': 0, 'end': 0, 'words': []}
        
        for word in words:
            word_text = word.get('word', '')
            word_start = word.get('start', 0)
            word_end = word.get('end', 0)
            
            if not current_segment['text']:
                current_segment['start'] = word_start
            
            current_segment['text'] += word_text + ' '
            current_segment['end'] = word_end
            current_segment['words'].append(word)
            
            if (word_end - current_segment['start'] > max_duration or 
                word_text.endswith('.') or word_text.endswith('?') or word_text.endswith('!')):
                
                segments.append({
                    'text': current_segment['text'].strip(),
                    'start': current_segment['start'],
                    'end': current_segment['end']
                })
                
                current_segment = {'text': '', 'start': 0, 'end': 0, 'words': []}
        
        if current_segment['text']:
            segments.append({
                'text': current_segment['text'].strip(),
                'start': current_segment['start'],
                'end': current_segment['end']
            })
        
        return segments