"""
Test suite for AI Content Management application.
"""

import os
import sys
import json
from pathlib import Path
import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.file_handler import FileHandler, FileHandlerError
from src.processors import TextProcessor, ProcessorError
from src.output_manager import OutputManager, OutputManagerError


# Test fixtures
@pytest.fixture
def sample_txt_file():
    """Path to sample text file."""
    return os.path.join('sample_files', 'ai_overview.txt')


@pytest.fixture
def sample_negative_review():
    """Path to negative review file for sentiment analysis."""
    return os.path.join('sample_files', 'negative_review.txt')


@pytest.fixture
def sample_climate_file():
    """Path to climate change file for translation."""
    return os.path.join('sample_files', 'climate_change.txt')


class TestFileHandler:
    """Test file handling functionality."""
    
    def test_validate_existing_file(self, sample_txt_file):
        """Test validation of existing file."""
        if os.path.exists(sample_txt_file):
            path = FileHandler.validate_file_path(sample_txt_file)
            assert path.exists()
            assert path.is_file()
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        with pytest.raises(FileHandlerError):
            FileHandler.validate_file_path('/path/to/nonexistent/file.txt')
    
    def test_validate_unsupported_extension(self, tmp_path):
        """Test validation of unsupported file type."""
        # Create a temporary .doc file
        temp_file = tmp_path / "test.doc"
        temp_file.write_text("test content")
        
        with pytest.raises(FileHandlerError, match="Unsupported file type"):
            FileHandler.validate_file_path(str(temp_file))
    
    def test_read_txt_file(self, sample_txt_file):
        """Test reading text file."""
        if os.path.exists(sample_txt_file):
            content, filename = FileHandler.read_file(sample_txt_file)
            assert len(content) > 0
            assert isinstance(content, str)
            assert filename == 'ai_overview'
    
    def test_word_count(self, sample_txt_file):
        """Test word counting."""
        if os.path.exists(sample_txt_file):
            content, _ = FileHandler.read_file(sample_txt_file)
            word_count = FileHandler.get_word_count(content)
            assert word_count > 0
            assert isinstance(word_count, int)


class TestOutputManager:
    """Test output management functionality."""
    
    def test_generate_filename(self):
        """Test filename generation."""
        from datetime import datetime
        
        timestamp = datetime(2025, 11, 12, 15, 30, 45)
        filename = OutputManager.generate_filename('test', 'summarize', timestamp)
        
        assert filename == 'test_summarize_2025-11-12_15-30-45.json'
    
    def test_validate_schema_valid(self):
        """Test schema validation with valid data."""
        data = {
            'file': 'test.txt',
            'use_case': 'summarize',
            'timestamp': '2025-11-12T15:30:45',
            'result': {'summary': 'Test'},
            'word_count': 100,
            'language_detected': 'English'
        }
        
        # Should not raise exception
        OutputManager.validate_output_schema(data)
    
    def test_validate_schema_missing_field(self):
        """Test schema validation with missing field."""
        data = {
            'file': 'test.txt',
            'use_case': 'summarize',
            'timestamp': '2025-11-12T15:30:45',
            'result': {'summary': 'Test'},
            'word_count': 100
            # Missing 'language_detected'
        }
        
        with pytest.raises(OutputManagerError, match="missing required fields"):
            OutputManager.validate_output_schema(data)
    
    def test_validate_schema_invalid_use_case(self):
        """Test schema validation with invalid use case."""
        data = {
            'file': 'test.txt',
            'use_case': 'invalid',
            'timestamp': '2025-11-12T15:30:45',
            'result': {'summary': 'Test'},
            'word_count': 100,
            'language_detected': 'English'
        }
        
        with pytest.raises(OutputManagerError, match="Invalid use_case"):
            OutputManager.validate_output_schema(data)
    
    def test_ensure_output_directory(self):
        """Test output directory creation."""
        output_dir = OutputManager.ensure_output_directory()
        assert output_dir.exists()
        assert output_dir.is_dir()


class TestIntegration:
    """Integration tests for complete workflows."""
    
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set"
    )
    def test_summarization_workflow(self, sample_txt_file):
        """Test complete summarization workflow."""
        if not os.path.exists(sample_txt_file):
            pytest.skip("Sample file not found")
        
        # Initialize processor
        processor = TextProcessor()
        
        # Process file
        result = processor.process_summarization(sample_txt_file)
        
        # Validate result structure
        assert 'filename' in result
        assert 'use_case' in result
        assert 'result' in result
        assert 'word_count' in result
        assert 'language_detected' in result
        
        # Validate use case
        assert result['use_case'] == 'summarize'
        
        # Validate summary result
        assert 'summary' in result['result']
        assert 'key_points' in result['result']
        assert isinstance(result['result']['key_points'], list)
        assert 3 <= len(result['result']['key_points']) <= 5
        
        # Test saving
        output_path = OutputManager.save_from_processor_result(result)
        assert os.path.exists(output_path)
        
        # Validate saved JSON
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['use_case'] == 'summarize'
        assert 'timestamp' in saved_data
        
        print(f"\n✓ Summarization test passed")
        print(f"  Summary: {result['result']['summary'][:100]}...")
        print(f"  Key points: {len(result['result']['key_points'])}")
        print(f"  Saved to: {output_path}")
    
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set"
    )
    def test_translation_workflow(self, sample_climate_file):
        """Test complete translation workflow."""
        if not os.path.exists(sample_climate_file):
            pytest.skip("Sample file not found")
        
        # Initialize processor
        processor = TextProcessor()
        
        # Process file
        result = processor.process_translation(sample_climate_file, "Spanish")
        
        # Validate result structure
        assert result['use_case'] == 'translate'
        assert 'translated_text' in result['result']
        assert 'target_language' in result['result']
        assert result['result']['target_language'] == 'Spanish'
        
        # Test saving
        output_path = OutputManager.save_from_processor_result(result)
        assert os.path.exists(output_path)
        
        print(f"\n✓ Translation test passed")
        print(f"  Target language: {result['result']['target_language']}")
        print(f"  Translation preview: {result['result']['translated_text'][:100]}...")
        print(f"  Saved to: {output_path}")
    
    @pytest.mark.skipif(
        not os.getenv('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set"
    )
    def test_sentiment_workflow(self, sample_negative_review):
        """Test complete sentiment analysis workflow."""
        if not os.path.exists(sample_negative_review):
            pytest.skip("Sample file not found")
        
        # Initialize processor
        processor = TextProcessor()
        
        # Process file
        result = processor.process_sentiment(sample_negative_review)
        
        # Validate result structure
        assert result['use_case'] == 'sentiment'
        assert 'sentiment' in result['result']
        assert 'confidence' in result['result']
        assert 'explanation' in result['result']
        
        # Validate sentiment values
        assert result['result']['sentiment'] in ['positive', 'neutral', 'negative']
        assert 0 <= result['result']['confidence'] <= 1
        
        # Test saving
        output_path = OutputManager.save_from_processor_result(result)
        assert os.path.exists(output_path)
        
        print(f"\n✓ Sentiment analysis test passed")
        print(f"  Sentiment: {result['result']['sentiment']}")
        print(f"  Confidence: {result['result']['confidence']:.2%}")
        print(f"  Explanation: {result['result']['explanation'][:100]}...")
        print(f"  Saved to: {output_path}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
