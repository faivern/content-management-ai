"""
Output manager module: Handles saving processing results to JSON files.

This module is responsible for:
- Creating and managing the output directory
- Generating timestamped filenames to avoid overwrites
- Validating output data against a required schema
- Saving results in a consistent, structured JSON format

All processing results go through this module before being saved to disk.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class OutputManagerError(Exception):
    """
    Custom exception for output manager errors.
    
    Raised when:
    - Output data fails schema validation
    - File system operations fail (permissions, disk full, etc.)
    - Invalid use_case values are provided
    """
    pass


class OutputManager:
    """
    Manages saving processing results to JSON files with validation and organization.
    
    This class ensures all output files:
    - Have consistent naming (filename_usecase_timestamp.json)
    - Include all required metadata fields
    - Are saved to a dedicated output/ directory
    - Use proper JSON formatting (indented, UTF-8)
    
    All methods are static/class methods since this is a utility class
    with no instance-specific state.
    """
    
    # Directory where all output files will be saved
    OUTPUT_DIR = 'output'
    
    # Required schema fields for validation
    # Every output JSON must have these fields to be considered valid
    REQUIRED_FIELDS = [
        'file',              # Original filename
        'use_case',          # Type of processing (summarize/translate/sentiment)
        'timestamp',         # When the processing occurred
        'result',            # The actual AI-generated result
        'word_count',        # Statistics about the source text
        'language_detected'  # What language was detected
    ]
    
    @staticmethod
    def ensure_output_directory() -> Path:
        """
        Create the output directory if it doesn't exist yet.
        
        Uses exist_ok=True to avoid errors if the directory already exists.
        This is called before every save operation to ensure the destination exists.
        
        Returns:
            Path object pointing to the output directory
            
        Example:
            path = ensure_output_directory()
            # Returns: Path('output')
            # Side effect: Creates 'output/' directory if it doesn't exist
        """
        output_path = Path(OutputManager.OUTPUT_DIR)
        # mkdir with exist_ok=True is safe to call multiple times
        output_path.mkdir(exist_ok=True)
        return output_path
    
    @staticmethod
    def generate_filename(base_name: str, use_case: str, timestamp: datetime) -> str:
        """
        Generate a unique, timestamped filename for output files.
        
        The timestamp ensures files never overwrite each other, even if processing
        the same file multiple times. The format is human-readable and sorts
        chronologically when listed in a file browser.
        
        Args:
            base_name: Original filename without extension (e.g., "article" from "article.txt")
            use_case: Type of processing (summarize/translate/sentiment)
            timestamp: When the processing occurred
            
        Returns:
            Formatted filename string
            
        Example:
            filename = generate_filename("article", "summarize", datetime.now())
            # Returns: "article_summarize_2024-01-15_14-30-45.json"
        """
        # Format timestamp as YYYY-MM-DD_HH-MM-SS (filesystem-safe, sortable)
        # Using hyphens instead of colons because Windows doesn't allow colons in filenames
        time_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        
        # Combine all parts: original_name + operation + timestamp + extension
        return f"{base_name}_{use_case}_{time_str}.json"
    
    @staticmethod
    def validate_output_schema(data: Dict[str, Any]) -> None:
        """
        Validate that output data contains all required fields and correct data types.
        
        This acts as a quality gate before saving files. It catches:
        - Missing required fields (programming errors in processors)
        - Invalid use_case values (typos or unsupported operations)
        - Wrong data types (e.g., word_count as string instead of int)
        
        Args:
            data: Dictionary to validate before saving
            
        Raises:
            OutputManagerError: If validation fails (descriptive message included)
            
        Example:
            # Valid data passes silently:
            validate_output_schema({
                'file': 'test.txt',
                'use_case': 'summarize',
                'timestamp': '2024-01-15T14:30:00',
                'result': {...},
                'word_count': 100,
                'language_detected': 'English'
            })
            
            # Invalid data raises error:
            validate_output_schema({'file': 'test.txt'})
            # Raises: OutputManagerError("Output data missing required fields: use_case, ...")
        """
        # Check for missing required fields using list comprehension
        # This is more efficient than checking each field individually
        missing_fields = [
            field for field in OutputManager.REQUIRED_FIELDS 
            if field not in data
        ]
        
        if missing_fields:
            # Programming error: a processor didn't include all required fields
            raise OutputManagerError(
                f"Output data missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate use_case value against allowed values
        # This prevents typos like "summerize" from going unnoticed
        valid_use_cases = ['summarize', 'translate', 'sentiment']
        if data['use_case'] not in valid_use_cases:
            raise OutputManagerError(
                f"Invalid use_case: {data['use_case']}. "
                f"Must be one of: {', '.join(valid_use_cases)}"
            )
        
        # Type validation: word_count must be an integer
        # This catches bugs where word count is accidentally a string or float
        if not isinstance(data['word_count'], int):
            raise OutputManagerError("word_count must be an integer")
    
    @staticmethod
    def prepare_output_data(
        filename: str,
        use_case: str,
        result: Dict[str, Any],
        word_count: int,
        language_detected: str
    ) -> Dict[str, Any]:
        """
        Prepare and structure output data with timestamp.
        
        This creates the final JSON structure that will be saved to disk.
        It adds a current timestamp and organizes all data into the standard format.
        
        Args:
            filename: Original filename (without extension)
            use_case: Type of processing performed
            result: The AI-generated result (structure varies by use case)
            word_count: Number of words in the source text
            language_detected: Detected language of source text
            
        Returns:
            Complete, structured output dictionary ready for saving
            
        Example:
            data = prepare_output_data(
                "article", "summarize", 
                {'summary': '...', 'key_points': [...]},
                250, "English"
            )
            # Returns: {
            #     'file': 'article',
            #     'use_case': 'summarize',
            #     'timestamp': '2024-01-15T14:30:00.123456',
            #     'result': {...},
            #     'word_count': 250,
            #     'language_detected': 'English'
            # }
        """
        # Capture the current moment in ISO format
        # ISO format is timezone-aware and universally parseable
        timestamp = datetime.now()
        
        # Build the standard output structure
        # This structure is consistent across all use cases
        output_data = {
            'file': filename,
            'use_case': use_case,
            'timestamp': timestamp.isoformat(),  # ISO 8601 format (e.g., "2024-01-15T14:30:00.123456")
            'result': result,  # The actual AI result (varies by use case)
            'word_count': word_count,
            'language_detected': language_detected
        }
        
        return output_data
    
    @classmethod
    def save_result(
        cls,
        filename: str,
        use_case: str,
        result: Dict[str, Any],
        word_count: int,
        language_detected: str
    ) -> str:
        """
        Save processing result to a JSON file (main save method).
        
        This orchestrates the complete save workflow:
        1. Prepare the data structure
        2. Validate against schema
        3. Create output directory if needed
        4. Generate unique filename
        5. Write to disk in pretty-printed JSON format
        
        Args:
            filename: Original filename without extension
            use_case: Type of processing (summarize/translate/sentiment)
            result: The AI-generated result dictionary
            word_count: Number of words in source text
            language_detected: Detected language
            
        Returns:
            String path to the saved file (e.g., "output/article_summarize_2024-01-15_14-30-00.json")
            
        Raises:
            OutputManagerError: If validation or file save fails
            
        Example:
            path = OutputManager.save_result(
                "article",
                "summarize",
                {'summary': '...', 'key_points': [...]},
                250,
                "English"
            )
            # Returns: "output/article_summarize_2024-01-15_14-30-00.json"
            # Side effect: Creates JSON file in output/ directory
        """
        try:
            # Step 1: Prepare the complete data structure with timestamp
            output_data = cls.prepare_output_data(
                filename, use_case, result, word_count, language_detected
            )
            
            # Step 2: Validate against required schema
            # This catches bugs before writing to disk
            cls.validate_output_schema(output_data)
            
            # Step 3: Ensure output directory exists (creates if needed)
            output_dir = cls.ensure_output_directory()
            
            # Step 4: Generate timestamped filename
            # Need to convert ISO string back to datetime for filename generation
            timestamp = datetime.fromisoformat(output_data['timestamp'])
            output_filename = cls.generate_filename(filename, use_case, timestamp)
            output_path = output_dir / output_filename
            
            # Step 5: Write to disk
            # Using UTF-8 encoding to support all languages
            # indent=2 makes the JSON human-readable
            # ensure_ascii=False allows Unicode characters (important for non-English text)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            # Return the path as a string for display to user
            return str(output_path)
            
        except OutputManagerError:
            # Re-raise our own errors (already have good messages)
            raise
        except Exception as e:
            # Catch unexpected errors (file permissions, disk full, etc.)
            raise OutputManagerError(f"Error saving output file: {str(e)}")
    
    @classmethod
    def save_from_processor_result(cls, processor_result: Dict[str, Any]) -> str:
        """
        Convenience method to save results directly from processor output format.
        
        TextProcessor returns a specific dictionary structure. This method
        unpacks that structure and calls the main save_result() method.
        This makes the CLI code cleaner by providing a simpler interface.
        
        Args:
            processor_result: Complete result dictionary from TextProcessor
                             (must have: filename, use_case, result, word_count, language_detected)
            
        Returns:
            Path to the saved file
            
        Raises:
            OutputManagerError: If processor_result is missing required fields or save fails
            
        Example:
            # From CLI after processing:
            result = processor.process_summarization("article.txt")
            path = OutputManager.save_from_processor_result(result)
            # Unpacks and saves in one call
        """
        try:
            # Unpack the processor result dictionary and pass to main save method
            # Using KeyError to catch missing fields early
            return cls.save_result(
                filename=processor_result['filename'],
                use_case=processor_result['use_case'],
                result=processor_result['result'],
                word_count=processor_result['word_count'],
                language_detected=processor_result['language_detected']
            )
        except KeyError as e:
            # Programming error: processor returned incomplete data
            raise OutputManagerError(f"Missing required field in processor result: {str(e)}")
