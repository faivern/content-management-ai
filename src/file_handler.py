"""
File handler module for reading .txt and .pdf files.
Validates file paths and extracts text content.

This module provides a unified interface for reading both text and PDF files,
with built-in validation and error handling. It's the entry point for all
file operations in the application.
"""

import os
from pathlib import Path
from typing import Optional
from pypdf import PdfReader


class FileHandlerError(Exception):
    """Custom exception for file handling errors.
    
    Raised when file operations fail (e.g., file not found, unsupported format,
    empty files, or corrupted PDFs). This allows the calling code to distinguish
    file errors from other types of errors.
    """
    pass


class FileHandler:
    """Handles file reading operations for .txt and .pdf files.
    
    This class provides static methods for validating and reading files.
    All methods are static because they don't need to maintain state between calls.
    """
    
    # List of file extensions this handler supports
    # Making this a class constant allows easy extension in the future
    SUPPORTED_EXTENSIONS = ['.txt', '.pdf']
    
    @staticmethod
    def validate_file_path(file_path: str) -> Path:
        """
        Validate that the file exists and has a supported extension.
        
        Args:
            file_path: Absolute path to the file
            
        Returns:
            Path object if valid
            
        Raises:
            FileHandlerError: If file doesn't exist or has unsupported extension
        """
        path = Path(file_path)
        
        # Check if file exists
        if not path.exists():
            raise FileHandlerError(f"File not found: {file_path}")
        
        # Check if it's a file (not a directory)
        if not path.is_file():
            raise FileHandlerError(f"Path is not a file: {file_path}")
        
        # Check file extension
        if path.suffix.lower() not in FileHandler.SUPPORTED_EXTENSIONS:
            raise FileHandlerError(
                f"Unsupported file type: {path.suffix}. "
                f"Supported types: {', '.join(FileHandler.SUPPORTED_EXTENSIONS)}"
            )
        
        return path
    
    @staticmethod
    def read_txt_file(file_path: Path) -> str:
        """
        Read content from a .txt file with automatic encoding detection.
        
        This method tries UTF-8 first (the most common encoding), then falls back
        to Latin-1 if UTF-8 fails. This handles most text files gracefully.
        
        Args:
            file_path: Path to the .txt file
            
        Returns:
            File content as string
            
        Raises:
            FileHandlerError: If file cannot be read or is empty
        """
        try:
            # Try UTF-8 first (most common encoding for modern text files)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Reject empty files to avoid processing nothing
            if not content.strip():
                raise FileHandlerError("File is empty")
            
            return content
        except UnicodeDecodeError:
            # If UTF-8 fails, try Latin-1 (handles older/special character files)
            # Latin-1 never fails because it maps all byte values to characters
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return content
            except Exception as e:
                raise FileHandlerError(f"Error reading file with encoding: {str(e)}")
        except Exception as e:
            raise FileHandlerError(f"Error reading .txt file: {str(e)}")
    
    @staticmethod
    def read_pdf_file(file_path: Path) -> str:
        """
        Extract text content from a .pdf file.
        
        Important: This only works with PDFs that contain actual text.
        Scanned PDFs (images of text) require OCR and are not supported.
        
        Args:
            file_path: Path to the .pdf file
            
        Returns:
            Extracted text as string (text from all pages combined)
            
        Raises:
            FileHandlerError: If PDF cannot be read, is empty, or has no extractable text
        """
        try:
            # Open in binary mode ('rb') because PDFs are binary files
            with open(file_path, 'rb') as f:
                pdf_reader = PdfReader(f)
                
                # Check for empty PDF
                if len(pdf_reader.pages) == 0:
                    raise FileHandlerError("PDF file has no pages")
                
                # Extract text from each page and collect in a list
                # Some pages might have no text, so we filter those out
                text_parts = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:  # Only add non-empty text
                        text_parts.append(text)
                
                # Join all pages with newlines to maintain document structure
                content = '\n'.join(text_parts)
                
                # If we got no text from any page, the PDF might be scanned/image-based
                if not content.strip():
                    raise FileHandlerError("Could not extract text from PDF")
                
                return content
        except Exception as e:
            # Check if it's a PDF-specific error (corrupted file, wrong format, etc.)
            if "PDF" in str(type(e).__name__):
                raise FileHandlerError(f"Invalid or corrupted PDF file: {str(e)}")
            raise FileHandlerError(f"Error reading .pdf file: {str(e)}")
    
    @classmethod
    def read_file(cls, file_path: str) -> tuple[str, str]:
        """
        Read content from a file (auto-detects .txt or .pdf).
        
        This is the main entry point for reading files. It automatically
        determines the file type and calls the appropriate reader method.
        
        Args:
            file_path: Absolute path to the file
            
        Returns:
            Tuple of (content, filename) where:
            - content: The full text extracted from the file
            - filename: Just the name without extension (e.g., "report" from "report.pdf")
            
        Raises:
            FileHandlerError: If file cannot be read or has unsupported extension
        """
        # First validate the file exists and has a supported extension
        path = cls.validate_file_path(file_path)
        
        # Route to the appropriate reader based on file extension
        # .lower() ensures we handle both .TXT and .txt consistently
        if path.suffix.lower() == '.txt':
            content = cls.read_txt_file(path)
        elif path.suffix.lower() == '.pdf':
            content = cls.read_pdf_file(path)
        else:
            # This should never happen due to validation, but kept for safety
            raise FileHandlerError(f"Unsupported file type: {path.suffix}")
        
        # path.stem gives filename without extension (e.g., "document" from "document.pdf")
        # This is used for naming output files later
        return content, path.stem
    
    @staticmethod
    def get_word_count(text: str) -> int:
        """
        Count words in text using simple whitespace splitting.
        
        Note: This is a basic word counter that splits on whitespace.
        It may not be 100% accurate for all languages (e.g., Chinese, Japanese)
        but works well for most Western languages.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words (integer)
        """
        # split() with no arguments splits on any whitespace (spaces, tabs, newlines)
        # This means "hello  world" (double space) still counts as 2 words
        return len(text.split())
