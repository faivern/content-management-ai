"""
Output manager module for saving results to JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class OutputManagerError(Exception):
    """Custom exception for output manager errors."""
    pass


class OutputManager:
    """
    Manages saving processing results to JSON files with proper naming and validation.
    """
    
    OUTPUT_DIR = 'output'
    
    # Required schema fields for validation
    REQUIRED_FIELDS = [
        'file',
        'use_case',
        'timestamp',
        'result',
        'word_count',
        'language_detected'
    ]
    
    @staticmethod
    def ensure_output_directory() -> Path:
        """
        Ensure the output directory exists.
        
        Returns:
            Path to output directory
        """
        output_path = Path(OutputManager.OUTPUT_DIR)
        output_path.mkdir(exist_ok=True)
        return output_path
    
    @staticmethod
    def generate_filename(base_name: str, use_case: str, timestamp: datetime) -> str:
        """
        Generate a timestamped filename for output.
        
        Args:
            base_name: Base filename (without extension)
            use_case: Use case name (summarize, translate, sentiment)
            timestamp: Timestamp for the file
            
        Returns:
            Formatted filename
        """
        # Format: filename_usecase_YYYY-MM-DD_HH-MM-SS.json
        time_str = timestamp.strftime('%Y-%m-%d_%H-%M-%S')
        return f"{base_name}_{use_case}_{time_str}.json"
    
    @staticmethod
    def validate_output_schema(data: Dict[str, Any]) -> None:
        """
        Validate that the output data contains all required fields.
        
        Args:
            data: Data to validate
            
        Raises:
            OutputManagerError: If validation fails
        """
        missing_fields = [
            field for field in OutputManager.REQUIRED_FIELDS 
            if field not in data
        ]
        
        if missing_fields:
            raise OutputManagerError(
                f"Output data missing required fields: {', '.join(missing_fields)}"
            )
        
        # Validate use_case value
        valid_use_cases = ['summarize', 'translate', 'sentiment']
        if data['use_case'] not in valid_use_cases:
            raise OutputManagerError(
                f"Invalid use_case: {data['use_case']}. "
                f"Must be one of: {', '.join(valid_use_cases)}"
            )
        
        # Validate word_count is a number
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
        Prepare output data with proper structure and timestamp.
        
        Args:
            filename: Original filename (without extension)
            use_case: Use case name
            result: Processing result
            word_count: Word count of source text
            language_detected: Detected language
            
        Returns:
            Structured output data
        """
        timestamp = datetime.now()
        
        output_data = {
            'file': filename,
            'use_case': use_case,
            'timestamp': timestamp.isoformat(),
            'result': result,
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
        Save processing result to a JSON file.
        
        Args:
            filename: Original filename (without extension)
            use_case: Use case name
            result: Processing result
            word_count: Word count of source text
            language_detected: Detected language
            
        Returns:
            Path to the saved file
            
        Raises:
            OutputManagerError: If saving fails
        """
        try:
            # Prepare output data
            output_data = cls.prepare_output_data(
                filename, use_case, result, word_count, language_detected
            )
            
            # Validate schema
            cls.validate_output_schema(output_data)
            
            # Ensure output directory exists
            output_dir = cls.ensure_output_directory()
            
            # Generate filename with timestamp
            timestamp = datetime.fromisoformat(output_data['timestamp'])
            output_filename = cls.generate_filename(filename, use_case, timestamp)
            output_path = output_dir / output_filename
            
            # Save to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            return str(output_path)
            
        except OutputManagerError:
            raise
        except Exception as e:
            raise OutputManagerError(f"Error saving output file: {str(e)}")
    
    @classmethod
    def save_from_processor_result(cls, processor_result: Dict[str, Any]) -> str:
        """
        Save result from processor output format.
        
        Args:
            processor_result: Result dict from TextProcessor
            
        Returns:
            Path to the saved file
            
        Raises:
            OutputManagerError: If saving fails
        """
        try:
            return cls.save_result(
                filename=processor_result['filename'],
                use_case=processor_result['use_case'],
                result=processor_result['result'],
                word_count=processor_result['word_count'],
                language_detected=processor_result['language_detected']
            )
        except KeyError as e:
            raise OutputManagerError(f"Missing required field in processor result: {str(e)}")
