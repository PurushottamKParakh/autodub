from openai import OpenAI
import os

class Translator:
    """Service for translating text using OpenAI"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        # Initialize OpenAI client without proxies parameter
        try:
            self.client = OpenAI(api_key=self.api_key, max_retries=2, timeout=60.0)
        except TypeError:
            # Fallback for older SDK versions
            self.client = OpenAI(api_key=self.api_key)
    
    def translate_text(self, text, target_language, source_language='en'):
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code or name
            source_language: Source language code or name
            
        Returns:
            str: Translated text
        """
        try:
            language_map = {
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
            
            target_lang_name = language_map.get(target_language.lower(), target_language)
            source_lang_name = language_map.get(source_language.lower(), source_language)
            
            prompt = f"Translate the following text from {source_lang_name} to {target_lang_name}. Maintain the tone and style. Only return the translation, nothing else:\n\n{text}"
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a professional translator. Translate text from {source_lang_name} to {target_lang_name} accurately while preserving meaning, tone, and style."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translated_text = response.choices[0].message.content.strip()
            return translated_text
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    def translate_segments(self, segments, target_language, source_language='en'):
        """
        Translate multiple segments while preserving structure
        
        Args:
            segments: List of segments with text and timestamps
            target_language: Target language code
            source_language: Source language code
            
        Returns:
            list: Translated segments with original timestamps
        """
        translated_segments = []
        
        for segment in segments:
            try:
                translated_text = self.translate_text(
                    segment['text'],
                    target_language,
                    source_language
                )
                
                translated_segments.append({
                    'original_text': segment['text'],
                    'translated_text': translated_text,
                    'start': segment['start'],
                    'end': segment['end'],
                    'speaker': segment.get('speaker', 0)  # Preserve speaker info
                })
                
            except Exception as e:
                print(f"Warning: Failed to translate segment: {str(e)}")
                # Keep original text if translation fails
                translated_segments.append({
                    'original_text': segment['text'],
                    'translated_text': segment['text'],
                    'start': segment['start'],
                    'end': segment['end'],
                    'speaker': segment.get('speaker', 0)  # Preserve speaker info
                })
        
        return translated_segments
    
    def batch_translate_segments(self, segments, target_language, source_language='en', batch_size=5):
        """
        Translate segments in batches for efficiency
        
        Args:
            segments: List of segments
            target_language: Target language
            source_language: Source language
            batch_size: Number of segments to translate at once
            
        Returns:
            list: Translated segments
        """
        translated_segments = []
        
        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            
            # Combine texts with markers
            combined_text = "\n---\n".join([seg['text'] for seg in batch])
            
            try:
                translated_combined = self.translate_text(
                    combined_text,
                    target_language,
                    source_language
                )
                
                # Split back into segments
                translated_texts = translated_combined.split("\n---\n")
                
                for j, segment in enumerate(batch):
                    translated_text = translated_texts[j] if j < len(translated_texts) else segment['text']
                    
                    translated_segments.append({
                        'original_text': segment['text'],
                        'translated_text': translated_text.strip(),
                        'start': segment['start'],
                        'end': segment['end'],
                        'speaker': segment.get('speaker', 0)  # Preserve speaker info
                    })
                    
            except Exception as e:
                print(f"Warning: Batch translation failed, falling back to individual: {str(e)}")
                # Fallback to individual translation
                for segment in batch:
                    try:
                        translated_text = self.translate_text(
                            segment['text'],
                            target_language,
                            source_language
                        )
                    except:
                        translated_text = segment['text']
                    
                    translated_segments.append({
                        'original_text': segment['text'],
                        'translated_text': translated_text,
                        'start': segment['start'],
                        'end': segment['end'],
                        'speaker': segment.get('speaker', 0)  # Preserve speaker info
                    })
        
        return translated_segments
