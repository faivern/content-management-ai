"""
Processors module: Orchestrates complete workflows for text processing use cases.

This module sits between the CLI interface and the lower-level components
(file_handler and api_client). It's responsible for:
- Coordinating multi-step workflows (read file → detect language → process)
- Combining data from multiple sources (file metadata + API results)
- Error handling and translation across layers
- Building the final output structure with all metadata

Think of this as the "controller" or "orchestrator" layer in the architecture.
"""

from typing import Dict, Any
from .api_client import APIClient, APIClientError
from .file_handler import FileHandler, FileHandlerError


class ProcessorError(Exception):
    """
    Custom exception for processor errors.
    
    Raised when workflows fail at any step (file reading, API calls, etc.).
    This provides a unified error type for the CLI layer to handle.
    """
    pass


class TextProcessor:
    """
    Orchestrates text processing workflows for different use cases.
    
    This class coordinates all the steps needed to process a file:
    1. Read the file content
    2. Detect the language
    3. Perform the requested operation (summarize/translate/sentiment)
    4. Package results with metadata
    
    Each workflow follows a similar pattern but has slight variations
    depending on the use case.
    """
    
    def __init__(self):
        """
        Initialize processor with API client.
        
        Raises:
            ProcessorError: If API client initialization fails (e.g., missing API key)
        """
        try:
            # Create the OpenAI API client
            # This will fail early if OPENAI_API_KEY is not set
            self.api_client = APIClient()
        except APIClientError as e:
            # Re-wrap the error as ProcessorError for consistency
            # This keeps the CLI layer from needing to know about APIClientError
            raise ProcessorError(f"Failed to initialize API client: {str(e)}")
    
    def process_summarization(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file for summarization (complete workflow).
        
        This orchestrates all steps: read file → detect language → summarize → package results.
        The output includes both the summary and useful metadata like word count and language.
        
        Args:
            file_path: Absolute or relative path to the file to summarize
            
        Returns:
            Dictionary with complete results and metadata:
                - 'filename': Name of the processed file
                - 'use_case': Always "summarize" (for output_manager)
                - 'result': The summary dict from api_client (summary + key_points)
                - 'word_count': Number of words in original text
                - 'language_detected': Detected language of the source text
            
        Raises:
            ProcessorError: If any step fails (file reading, language detection, summarization)
            
        Example:
            processor = TextProcessor()
            result = processor.process_summarization("article.txt")
            # Returns: {
            #     'filename': 'article.txt',
            #     'use_case': 'summarize',
            #     'result': {'summary': '...', 'key_points': [...]},
            #     'word_count': 523,
            #     'language_detected': 'English'
            # }
        """
        try:
            # Step 1: Read the file content
            # Returns both content (str) and filename (for metadata)
            content, filename = FileHandler.read_file(file_path)
            
            # Step 2: Detect what language the text is in
            # This happens before summarization so we can include it in metadata
            language = self.api_client.detect_language(content)
            
            # Step 3: Count words for statistics
            # Useful for users to compare original length vs summary
            word_count = FileHandler.get_word_count(content)
            
            # Step 4: Perform the actual summarization
            # Returns: {'summary': str, 'key_points': list}
            summary_result = self.api_client.summarize(content)
            
            # Step 5: Package everything into a structured result
            # This structure matches what output_manager expects
            return {
                'filename': filename,
                'use_case': 'summarize',  # Identifies the operation type
                'result': summary_result,  # The actual summary data
                'word_count': word_count,  # Metadata
                'language_detected': language  # Metadata
            }
            
        except FileHandlerError as e:
            # File reading failed (doesn't exist, wrong format, encoding issues, etc.)
            raise ProcessorError(f"File handling error: {str(e)}")
        except APIClientError as e:
            # API call failed (network, authentication, rate limits, etc.)
            raise ProcessorError(f"API error: {str(e)}")
        except Exception as e:
            # Unexpected error - catch-all for safety
            raise ProcessorError(f"Unexpected error during summarization: {str(e)}")
    
    def process_translation(self, file_path: str, target_language: str) -> Dict[str, Any]:
        """
        Process a file for translation (complete workflow).
        
        This orchestrates: read file → detect source language → translate → package results.
        Unlike summarization, this needs the target language as input from the user.
        
        Args:
            file_path: Absolute or relative path to the file to translate
            target_language: Name of the target language (e.g., "Spanish", "French")
            
        Returns:
            Dictionary with complete results and metadata:
                - 'filename': Name of the processed file
                - 'use_case': Always "translate"
                - 'result': Translation dict with source_language, target_language, translated_text
                - 'word_count': Number of words in original text
                - 'language_detected': Detected source language
            
        Raises:
            ProcessorError: If any step fails
            
        Example:
            processor = TextProcessor()
            result = processor.process_translation("letter.txt", "Spanish")
            # Returns: {
            #     'filename': 'letter.txt',
            #     'use_case': 'translate',
            #     'result': {
            #         'source_language': 'English',
            #         'target_language': 'Spanish',
            #         'translated_text': '...'
            #     },
            #     'word_count': 150,
            #     'language_detected': 'English'
            # }
        """
        try:
            # Step 1: Read the file content
            content, filename = FileHandler.read_file(file_path)
            
            # Step 2: Detect the source language
            # This is detected separately and added to results for transparency
            source_language = self.api_client.detect_language(content)
            
            # Step 3: Count words in the original text
            word_count = FileHandler.get_word_count(content)
            
            # Step 4: Perform the translation
            # Returns: {'translated_text': str, 'target_language': str}
            translation_result = self.api_client.translate(content, target_language)
            
            # Step 5: Enhance the result by adding the detected source language
            # The API returns target_language, but we add source_language for completeness
            translation_result['source_language'] = source_language
            
            # Step 6: Package everything into final structure
            return {
                'filename': filename,
                'use_case': 'translate',
                'result': translation_result,  # Now has source + target + text
                'word_count': word_count,
                'language_detected': source_language
            }
            
        except FileHandlerError as e:
            raise ProcessorError(f"File handling error: {str(e)}")
        except APIClientError as e:
            raise ProcessorError(f"API error: {str(e)}")
        except Exception as e:
            raise ProcessorError(f"Unexpected error during translation: {str(e)}")
    
    def process_sentiment(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file for sentiment analysis (complete workflow).
        
        This orchestrates: read file → detect language → analyze sentiment → package results.
        Useful for analyzing customer reviews, feedback, social media posts, etc.
        
        Args:
            file_path: Absolute or relative path to the file to analyze
            
        Returns:
            Dictionary with complete results and metadata:
                - 'filename': Name of the processed file
                - 'use_case': Always "sentiment"
                - 'result': Sentiment dict (sentiment, confidence, explanation)
                - 'word_count': Number of words in the text
                - 'language_detected': Detected language of the text
            
        Raises:
            ProcessorError: If any step fails
            
        Example:
            processor = TextProcessor()
            result = processor.process_sentiment("review.txt")
            # Returns: {
            #     'filename': 'review.txt',
            #     'use_case': 'sentiment',
            #     'result': {
            #         'sentiment': 'positive',
            #         'confidence': 0.92,
            #         'explanation': 'Strong positive language...'
            #     },
            #     'word_count': 87,
            #     'language_detected': 'English'
            # }
        """
        try:
            # Step 1: Read the file content
            content, filename = FileHandler.read_file(file_path)
            
            # Step 2: Detect the language
            # Language detection helps ensure the AI understands the text correctly
            language = self.api_client.detect_language(content)
            
            # Step 3: Count words for statistics
            word_count = FileHandler.get_word_count(content)
            
            # Step 4: Perform sentiment analysis
            # Returns: {'sentiment': str, 'confidence': float, 'explanation': str}
            sentiment_result = self.api_client.analyze_sentiment(content)
            
            # Step 5: Package everything into final structure
            return {
                'filename': filename,
                'use_case': 'sentiment',
                'result': sentiment_result,
                'word_count': word_count,
                'language_detected': language
            }
            
        except FileHandlerError as e:
            raise ProcessorError(f"File handling error: {str(e)}")
        except APIClientError as e:
            raise ProcessorError(f"API error: {str(e)}")
        except Exception as e:
            raise ProcessorError(f"Unexpected error during sentiment analysis: {str(e)}")
