import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from typing import List, Dict
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os

class OCRService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
            print("Tesseract OCR is available")
        except Exception as e:
            print(f"Warning: Tesseract OCR check failed: {e}")
            print("Make sure Tesseract is installed and in PATH")
    
    async def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """Process PDF with OCR and return text sections with coordinates"""
        try:
            print(f"Starting OCR processing for: {pdf_path}")
            loop = asyncio.get_event_loop()
            
            # Convert PDF to images
            print("Converting PDF to images...")
            images = await loop.run_in_executor(
                self.executor,
                self._convert_pdf_to_images,
                str(pdf_path)
            )
            print(f"Converted {len(images)} pages to images")
            
            sections = []
            
            for page_num, image in enumerate(images):
                # Get OCR data with bounding boxes
                ocr_data = await loop.run_in_executor(
                    self.executor,
                    pytesseract.image_to_data,
                    image,
                    pytesseract.Output.DICT
                )
                
                # Process OCR results
                current_text = ""
                current_x = 0
                current_y = 0
                current_width = 0
                current_height = 0
                
                for i in range(len(ocr_data['text'])):
                    text = ocr_data['text'][i].strip()
                    if text:
                        conf = int(ocr_data['conf'][i])
                        if conf > 30:  # Confidence threshold
                            x = ocr_data['left'][i]
                            y = ocr_data['top'][i]
                            w = ocr_data['width'][i]
                            h = ocr_data['height'][i]
                            
                            # Group nearby text into sections
                            if current_text and abs(y - current_y) < 10:
                                current_text += " " + text
                                current_width = max(current_width, x + w - current_x)
                                current_height = max(current_height, y + h - current_y)
                            else:
                                if current_text:
                                    sections.append({
                                        "id": f"section_{len(sections)}",
                                        "text": current_text,
                                        "x": current_x,
                                        "y": current_y,
                                        "width": current_width,
                                        "height": current_height,
                                        "page": page_num
                                    })
                                
                                current_text = text
                                current_x = x
                                current_y = y
                                current_width = w
                                current_height = h
                
                # Add last section
                if current_text:
                    sections.append({
                        "id": f"section_{len(sections)}",
                        "text": current_text,
                        "x": current_x,
                        "y": current_y,
                        "width": current_width,
                        "height": current_height,
                        "page": page_num
                    })
            
            print(f"OCR processing complete. Found {len(sections)} text sections")
            return sections
        except Exception as e:
            import traceback
            print(f"Error in OCR processing: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _convert_pdf_to_images(self, pdf_path: str):
        """Convert PDF to images with error handling"""
        try:
            # Check if poppler is available
            images = convert_from_path(
                pdf_path,
                dpi=200,  # Lower DPI for faster processing
                thread_count=2
            )
            return images
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            raise Exception(f"Failed to convert PDF to images. Make sure poppler-utils is installed. Error: {str(e)}")

