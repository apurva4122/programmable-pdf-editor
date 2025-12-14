import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from typing import List, Dict
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import os
import shutil

class OCRService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        # Configure Tesseract data path
        self._configure_tesseract()
        # Check if Tesseract is available
        try:
            version = pytesseract.get_tesseract_version()
            print(f"Tesseract OCR is available (version: {version})")
        except Exception as e:
            print(f"Warning: Tesseract OCR check failed: {e}")
            print("Make sure Tesseract is installed and in PATH")
    
    def _configure_tesseract(self):
        """Configure Tesseract data path for different environments"""
        # Common Tesseract data paths
        possible_paths = [
            "/usr/share/tesseract-ocr/5/tessdata",  # Ubuntu/Debian
            "/usr/share/tesseract-ocr/4.00/tessdata",  # Older Ubuntu
            "/usr/share/tesseract/tessdata",  # Some Linux
            "/opt/homebrew/share/tessdata",  # macOS Homebrew
            "/usr/local/share/tessdata",  # macOS/Linux
        ]
        
        # Check if TESSDATA_PREFIX is already set
        if os.environ.get("TESSDATA_PREFIX"):
            print(f"TESSDATA_PREFIX already set to: {os.environ.get('TESSDATA_PREFIX')}")
            return
        
        # Try to find Tesseract executable to determine data path
        tesseract_cmd = shutil.which("tesseract")
        if tesseract_cmd:
            print(f"Found Tesseract at: {tesseract_cmd}")
            # Try to get version and data path
            try:
                # Common pattern: if tesseract is at /usr/bin/tesseract, data might be at /usr/share/tesseract-ocr
                if "/usr/bin/tesseract" in tesseract_cmd:
                    for path in possible_paths:
                        if os.path.exists(path):
                            os.environ["TESSDATA_PREFIX"] = path
                            print(f"Set TESSDATA_PREFIX to: {path}")
                            return
            except:
                pass
        
        # Try each possible path
        for path in possible_paths:
            if os.path.exists(path):
                os.environ["TESSDATA_PREFIX"] = path
                print(f"Set TESSDATA_PREFIX to: {path}")
                return
        
        # If nothing found, try to use tesseract --print-parameters to find it
        try:
            import subprocess
            result = subprocess.run(
                ["tesseract", "--print-parameters"],
                capture_output=True,
                text=True,
                timeout=5
            )
            # Look for tessdata in output
            for line in result.stdout.split('\n'):
                if 'tessdata' in line.lower():
                    # Try to extract path
                    parts = line.split()
                    for part in parts:
                        if 'tessdata' in part:
                            potential_path = os.path.dirname(part) if os.path.isfile(part) else part
                            if os.path.exists(potential_path):
                                os.environ["TESSDATA_PREFIX"] = potential_path
                                print(f"Set TESSDATA_PREFIX to: {potential_path} (from tesseract --print-parameters)")
                                return
        except:
            pass
        
        print("Warning: Could not automatically detect TESSDATA_PREFIX. Tesseract may not work correctly.")
    
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
                # Specify language explicitly (default to 'eng' for English)
                ocr_data = await loop.run_in_executor(
                    self.executor,
                    lambda img: pytesseract.image_to_data(
                        img,
                        lang='eng',  # Explicitly set language
                        output_type=pytesseract.Output.DICT
                    ),
                    image
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

