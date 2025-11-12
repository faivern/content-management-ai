"""
File handler module for reading .txt and .pdf files.
Validates file paths and extracts text content.
"""

import os
from pathlib import Path
from typing import Optional
import PyPDF2


class FileHandlerError(Exception):
    """Custom exception for file handling errors."""
    pass


class FileHandler:
    """Handles file reading operations for .txt and .pdf files."""
    
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
        Read content from a .txt file.
        
        Args:
            file_path: Path to the .txt file
            
        Returns:
            File content as string
            
        Raises:
            FileHandlerError: If file cannot be read
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise FileHandlerError("File is empty")
            
            return content
        except UnicodeDecodeError:
            # Try with different encoding
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
        
        Args:
            file_path: Path to the .pdf file
            
        Returns:
            Extracted text as string
            
        Raises:
            FileHandlerError: If PDF cannot be read
        """
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                if len(pdf_reader.pages) == 0:
                    raise FileHandlerError("PDF file has no pages")
                
                # Extract text from all pages
                text_parts = []
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                
                content = '\n'.join(text_parts)
                
                if not content.strip():
                    raise FileHandlerError("Could not extract text from PDF")
                
                return content
        except PyPDF2.PdfReadError as e:
            raise FileHandlerError(f"Invalid or corrupted PDF file: {str(e)}")
        except Exception as e:
            raise FileHandlerError(f"Error reading .pdf file: {str(e)}")
    
    @classmethod
    def read_file(cls, file_path: str) -> tuple[str, str]:
        """
        Read content from a file (auto-detects .txt or .pdf).
        
        Args:
            file_path: Absolute path to the file
            
        Returns:
            Tuple of (content, filename)
            
        Raises:
            FileHandlerError: If file cannot be read
        """
        path = cls.validate_file_path(file_path)
        
        if path.suffix.lower() == '.txt':
            content = cls.read_txt_file(path)
        elif path.suffix.lower() == '.pdf':
            content = cls.read_pdf_file(path)
        else:
            raise FileHandlerError(f"Unsupported file type: {path.suffix}")
        
        return content, path.stem
    
    @staticmethod
    def get_word_count(text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Text to count words in
            
        Returns:
            Number of words
        """
        return len(text.split())
