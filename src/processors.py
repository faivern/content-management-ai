"""
Processors module for orchestrating use case workflows.
"""

from typing import Dict, Any
from .api_client import APIClient, APIClientError
from .file_handler import FileHandler, FileHandlerError


class ProcessorError(Exception):
    """Custom exception for processor errors."""
    pass


class TextProcessor:
    """
    Orchestrates text processing workflows for different use cases.
    """
    
    def __init__(self):
        """Initialize processor with API client."""
        try:
            self.api_client = APIClient()
        except APIClientError as e:
            raise ProcessorError(f"Failed to initialize API client: {str(e)}")
    
    def process_summarization(self, file_path: str) -> Dict[str, Any]:
        """
        Process a file for summarization.
        
        Args:
            file_path: Path to the file to summarize
            
        Returns:
            Dict containing summary results and metadata
            
        Raises:
            ProcessorError: If processing fails
        """
        try:
            # Read file
            content, filename = FileHandler.read_file(file_path)
            
            # Detect language
            language = self.api_client.detect_language(content)
            
            # Get word count
            word_count = FileHandler.get_word_count(content)
            
            # Perform summarization
            summary_result = self.api_client.summarize(content)
            
            return {
                'filename': filename,
                'use_case': 'summarize',
                'result': summary_result,
                'word_count': word_count,
                'language_detected': language
            }
            
        except FileHandlerError as e:
            raise ProcessorError(f"File handling error: {str(e)}")
        except APIClientError as e:
            raise ProcessorError(f"API error: {str(e)}")
        except Exception as e:
            raise ProcessorError(f"Unexpected error during summarization: {str(e)}")
    
    def process_translation(self, file_path: str, target_language: str) -> Dict[str, Any]:
        """
        Process a file for translation.
        
        Args:
            file_path: Path to the file to translate
            target_language: Target language for translation
            
        Returns:
            Dict containing translation results and metadata
            
        Raises:
            ProcessorError: If processing fails
        """
        try:
            # Read file
            content, filename = FileHandler.read_file(file_path)
            
            # Detect source language
            source_language = self.api_client.detect_language(content)
            
            # Get word count
            word_count = FileHandler.get_word_count(content)
            
            # Perform translation
            translation_result = self.api_client.translate(content, target_language)
            
            # Add source language to result
            translation_result['source_language'] = source_language
            
            return {
                'filename': filename,
                'use_case': 'translate',
                'result': translation_result,
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
        Process a file for sentiment analysis.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Dict containing sentiment results and metadata
            
        Raises:
            ProcessorError: If processing fails
        """
        try:
            # Read file
            content, filename = FileHandler.read_file(file_path)
            
            # Detect language
            language = self.api_client.detect_language(content)
            
            # Get word count
            word_count = FileHandler.get_word_count(content)
            
            # Perform sentiment analysis
            sentiment_result = self.api_client.analyze_sentiment(content)
            
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
