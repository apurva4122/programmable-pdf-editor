from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from pathlib import Path
from typing import Dict, List

try:
    import fitz  # PyMuPDF for better text replacement
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class PDFService:
    def __init__(self):
        pass
    
    def replace_text_in_pdf(self, pdf_path: Path, replacements: Dict[str, str]) -> bytes:
        """
        Replace text in PDF using PyMuPDF for better text replacement
        replacements: dict mapping original text to new text
        """
        if PYMUPDF_AVAILABLE:
            # Use PyMuPDF (better for text replacement)
            doc = fitz.open(str(pdf_path))
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                for old_text, new_text in replacements.items():
                    # Search for text instances
                    text_instances = page.search_for(old_text)
                    
                    for inst in text_instances:
                        # Add redaction annotation
                        page.add_redact_annot(inst)
                    
                    # Apply redactions
                    if text_instances:
                        page.apply_redactions()
                        
                        # Insert new text at the same position
                        for inst in text_instances:
                            # Get font size from original text
                            text_dict = page.get_text("dict")
                            font_size = 12  # Default
                            
                            # Try to find font size from text blocks
                            for block in text_dict["blocks"]:
                                if "lines" in block:
                                    for line in block["lines"]:
                                        for span in line["spans"]:
                                            if old_text in span.get("text", ""):
                                                font_size = span.get("size", 12)
                                                break
                            
                            # Insert new text
                            page.insert_text(
                                (inst.x0, inst.y0 + font_size),
                                new_text,
                                fontsize=font_size
                            )
            
            # Save to bytes
            pdf_bytes = doc.tobytes()
            doc.close()
            
            return pdf_bytes
        else:
            # Fallback to PyPDF2 if PyMuPDF not available
            return self._replace_text_pypdf2(pdf_path, replacements)
    
    def _replace_text_pypdf2(self, pdf_path: Path, replacements: Dict[str, str]) -> bytes:
        """Fallback method using PyPDF2"""
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        
        # Note: PyPDF2 has limited text replacement capabilities
        # This is a basic implementation
        for page in reader.pages:
            writer.add_page(page)
        
        output = BytesIO()
        writer.write(output)
        return output.getvalue()

