"""
OCR Handler for Contract Reviewer Crew

Handles Optical Character Recognition for image-based PDFs and scanned contracts.
Extracts text from images using Tesseract OCR engine.
"""

import os
import tempfile
from pathlib import Path
from typing import List, Optional

import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import pdfplumber


class OCRHandler:
    """Handles OCR operations for extracting text from images and image-based PDFs."""
    
    def __init__(self):
        """Initialize OCR handler with Tesseract configuration."""
        # Configure Tesseract for better contract text recognition
        self.tesseract_config = '--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:!?()[]{}"\'-/$%&@#*+=<>|\\~`^_ \n\t'
    
    def is_pdf_image_based(self, pdf_path: str) -> bool:
        """
        Check if PDF contains primarily images (scanned) vs text.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            bool: True if PDF appears to be image-based
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_chars = 0
                total_pages = len(pdf.pages)
                
                # Check first few pages for text content
                pages_to_check = min(3, total_pages)
                
                for page_num in range(pages_to_check):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_chars += len(text.strip())
                
                # If very little text found, likely image-based
                return text_chars < 50
                
        except Exception:
            # If we can't read it normally, assume it's image-based
            return True
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from a single image using OCR.
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            str: Extracted text
        """
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image for better OCR
            image = self._enhance_image_for_ocr(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, config=self.tesseract_config)
            
            return text.strip()
            
        except Exception as e:
            print(f"❌ OCR failed for image {image_path}: {e}")
            return ""
    
    def extract_text_from_pdf_images(self, pdf_path: str) -> str:
        """
        Extract text from image-based PDF using OCR.
        
        Args:
            pdf_path (str): Path to PDF file
            
        Returns:
            str: Extracted text from all pages
        """
        try:
            print("🔍 Converting PDF pages to images for OCR...")
            
            # Convert PDF pages to images
            with tempfile.TemporaryDirectory() as temp_dir:
                images = convert_from_path(
                    pdf_path,
                    dpi=300,  # High DPI for better OCR accuracy
                    fmt='PNG',
                    thread_count=2
                )
                
                print(f"📄 Processing {len(images)} pages with OCR...")
                
                all_text = []
                
                for page_num, image in enumerate(images, 1):
                    print(f"   Processing page {page_num}/{len(images)}...")
                    
                    # Save temporary image
                    temp_image_path = os.path.join(temp_dir, f"page_{page_num}.png")
                    image.save(temp_image_path)
                    
                    # Extract text from this page
                    page_text = self.extract_text_from_image(temp_image_path)
                    
                    if page_text.strip():
                        all_text.append(f"=== PAGE {page_num} ===\n{page_text}\n")
                    
                combined_text = "\n".join(all_text)
                
                if combined_text.strip():
                    print(f"✅ OCR completed: {len(combined_text)} characters extracted")
                    return combined_text
                else:
                    print("⚠️  OCR completed but no text was extracted")
                    return ""
                    
        except Exception as e:
            print(f"❌ PDF OCR failed: {e}")
            return ""
    
    def _enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Enhance image quality for better OCR results.
        
        Args:
            image: PIL Image object
            
        Returns:
            Enhanced PIL Image
        """
        try:
            # Convert to grayscale for better text recognition
            if image.mode != 'L':
                image = image.convert('L')
            
            # Resize if image is very small (improves OCR accuracy)
            width, height = image.size
            if width < 1000 or height < 1000:
                scale_factor = max(1000 / width, 1000 / height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"⚠️  Image enhancement failed: {e}")
            return image
    
    def extract_text_with_fallback(self, file_path: str) -> str:
        """
        Smart text extraction with OCR fallback for PDFs.
        
        Args:
            file_path (str): Path to PDF file
            
        Returns:
            str: Extracted text
        """
        try:
            # First, try normal PDF text extraction
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                # If we got substantial text, use it
                if len(text.strip()) > 100:
                    print(f"✅ Text extracted from PDF: {len(text)} characters")
                    return text
            
            # If little/no text found, check if it's image-based
            if self.is_pdf_image_based(file_path):
                print("📸 PDF appears to be image-based, using OCR...")
                return self.extract_text_from_pdf_images(file_path)
            else:
                print("⚠️  PDF has minimal text content")
                return text
                
        except Exception as e:
            print(f"❌ PDF processing failed: {e}")
            # Last resort: try OCR anyway
            print("🔄 Attempting OCR as last resort...")
            return self.extract_text_from_pdf_images(file_path)


# Global OCR handler instance
ocr_handler = OCRHandler()