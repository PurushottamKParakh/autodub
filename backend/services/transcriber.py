from deepgram import DeepgramClient, PrerecordedOptions
import os

class Transcriber:
    """Service for transcribing audio using Deepgram"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('DEEPGRAM_API_KEY')
        if not self.api_key:
            raise ValueError("Deepgram API key is required")
        self.client = DeepgramClient(self.api_key)
    
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
            with open(audio_path, 'rb') as audio_file:
                buffer_data = audio_file.read()
            
            payload = {'buffer': buffer_data}
            
            options = PrerecordedOptions(
                model='nova-2',
                language=language,
                smart_format=True,
                punctuate=True,
                paragraphs=True,
                utterances=True,
                diarize=True,  # Speaker diarization for multi-speaker support
            )
            
            response = self.client.listen.prerecorded.v('1').transcribe_file(
                payload, options
            )
            
            # Extract transcription with timestamps
            result = response.to_dict()
            
            # Parse the response
            transcription_data = self._parse_transcription(result)
            
            return transcription_data
            
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _parse_transcription(self, response):
        """
        Parse Deepgram response to extract text and timestamps
        
        Args:
            response: Deepgram API response
            
        Returns:
            dict: Parsed transcription data
        """
        try:
            results = response.get('results', {})
            channels = results.get('channels', [])
            
            if not channels:
                return {'segments': [], 'full_text': ''}
            
            alternatives = channels[0].get('alternatives', [])
            if not alternatives:
                return {'segments': [], 'full_text': ''}
            
            # Get words with timestamps
            words = alternatives[0].get('words', [])
            paragraphs = alternatives[0].get('paragraphs', {})
            
            # Extract full text
            full_text = alternatives[0].get('transcript', '')
            
            # Group words into segments (sentences/utterances)
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
                # Fallback: create segments from words
                segments = self._create_segments_from_words(words)
            
            return {
                'full_text': full_text,
                'segments': segments,
                'words': words
            }
            
        except Exception as e:
            raise Exception(f"Failed to parse transcription: {str(e)}")
    
    def _create_segments_from_words(self, words, max_duration=10):
        """
        Create segments from words when sentence info is not available
        
        Args:
            words: List of words with timestamps
            max_duration: Maximum duration per segment in seconds
            
        Returns:
            list: Segments with text and timestamps
        """
        segments = []
        current_segment = {
            'text': '',
            'start': 0,
            'end': 0,
            'words': []
        }
        
        for word in words:
            word_text = word.get('word', '')
            word_start = word.get('start', 0)
            word_end = word.get('end', 0)
            
            if not current_segment['text']:
                current_segment['start'] = word_start
            
            current_segment['text'] += word_text + ' '
            current_segment['end'] = word_end
            current_segment['words'].append(word)
            
            # Create new segment if duration exceeds max or sentence ends
            if (word_end - current_segment['start'] > max_duration or 
                word_text.endswith('.') or word_text.endswith('?') or word_text.endswith('!')):
                
                segments.append({
                    'text': current_segment['text'].strip(),
                    'start': current_segment['start'],
                    'end': current_segment['end']
                })
                
                current_segment = {
                    'text': '',
                    'start': 0,
                    'end': 0,
                    'words': []
                }
        
        # Add remaining segment
        if current_segment['text']:
            segments.append({
                'text': current_segment['text'].strip(),
                'start': current_segment['start'],
                'end': current_segment['end']
            })
        
        return segments
