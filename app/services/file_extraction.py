"""File extraction utilities for different file types"""

import io
import os
from typing import Tuple
from pathlib import Path

from app.core.logging_config import logger


class FileExtractor:
    """Extract text from various file types"""
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> str:
        """
        Extract text from file
        
        Args:
            file_path: Path to the file
            file_type: Type of file (pdf, txt, jpg, png, etc.)
            
        Returns:
            Extracted text
        """
        file_type = file_type.lower().strip('.')
        
        if file_type == 'pdf':
            return FileExtractor._extract_from_pdf(file_path)
        elif file_type == 'txt':
            return FileExtractor._extract_from_txt(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            return FileExtractor._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    @staticmethod
    def _extract_from_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        try:
            from pypdf import PdfReader
        except ImportError:
            logger.error("pypdf not installed. Install with: pip install pypdf")
            raise ImportError("pypdf is required for PDF extraction")
        
        try:
            text = ""
            with open(file_path, 'rb') as f:
                reader = PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            logger.info(f"Extracted text from PDF: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
    
    @staticmethod
    def _extract_from_txt(file_path: str) -> str:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            logger.info(f"Extracted text from TXT: {len(text)} characters")
            return text
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    text = f.read()
                logger.info(f"Extracted text from TXT (latin-1): {len(text)} characters")
                return text
            except Exception as e:
                logger.error(f"Error extracting TXT: {str(e)}")
                raise
    
    @staticmethod
    def _extract_from_image(file_path: str) -> str:
        """Extract text from image using OCR (Tesseract)"""
        try:
            import pytesseract
            from PIL import Image
        except ImportError:
            logger.error("pytesseract or Pillow not installed. Install with: pip install pytesseract pillow")
            raise ImportError("pytesseract and Pillow are required for image extraction")
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            logger.info(f"Extracted text from image: {len(text)} characters")
            return text
        except Exception as e:
            logger.error(f"Error extracting image: {str(e)}")
            raise
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """Get file type from filename"""
        _, ext = os.path.splitext(filename)
        return ext.lower().lstrip('.')


class FileValidator:
    """Validate file uploads"""
    
    ALLOWED_TYPES = ['pdf', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'bmp']
    MAX_SIZE = 50 * 1024 * 1024  # 50 MB
    
    @staticmethod
    def validate_file(filename: str, file_size: int) -> Tuple[bool, str]:
        """
        Validate file
        
        Args:
            filename: Name of the file
            file_size: Size of file in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check size
        if file_size > FileValidator.MAX_SIZE:
            return False, f"File too large. Max size: {FileValidator.MAX_SIZE / (1024*1024):.1f} MB"
        
        # Check file type
        file_type = FileExtractor.get_file_type(filename)
        if file_type not in FileValidator.ALLOWED_TYPES:
            return False, f"Unsupported file type: {file_type}. Allowed: {', '.join(FileValidator.ALLOWED_TYPES)}"
        
        return True, ""
