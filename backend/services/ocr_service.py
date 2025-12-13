import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from typing import List, Dict
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

class OCRService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_pdf(self, pdf_path: Path) -> List[Dict]:
        """Process PDF with OCR and return text sections with coordinates"""
        loop = asyncio.get_event_loop()
        
        # Convert PDF to images
        images = await loop.run_in_executor(
            self.executor,
            convert_from_path,
            str(pdf_path)
        )
        
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
        
        return sections

