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
        if not replacements:
            print("Warning: No replacements provided, returning original PDF")
            with open(pdf_path, "rb") as f:
                return f.read()
        
        print(f"Replacing {len(replacements)} text strings in PDF")
        
        if PYMUPDF_AVAILABLE:
            try:
                # Use PyMuPDF (better for text replacement)
                doc = fitz.open(str(pdf_path))
                print(f"Opened PDF with {len(doc)} pages")
                
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    print(f"Processing page {page_num + 1}/{len(doc)}")
                    
                    for old_text, new_text in replacements.items():
                        print(f"  Searching for: '{old_text}' -> '{new_text}'")
                        # Search for text instances
                        text_instances = page.search_for(old_text)
                        print(f"  Found {len(text_instances)} instances")
                        
                        if text_instances:
                            # Add redaction annotations
                            for inst in text_instances:
                                try:
                                    page.add_redact_annot(inst)
                                except Exception as e:
                                    print(f"    Warning: Could not add redaction: {e}")
                            
                            # Apply redactions
                            try:
                                page.apply_redactions()
                            except Exception as e:
                                print(f"    Warning: Redaction failed: {e}")
                            
                            # Insert new text at the same position
                            for inst in text_instances:
                                try:
                                    # Get font size from original text
                                    font_size = 12  # Default
                                    try:
                                        text_dict = page.get_text("dict")
                                        for block in text_dict.get("blocks", []):
                                            if "lines" in block:
                                                for line in block["lines"]:
                                                    for span in line.get("spans", []):
                                                        if old_text in span.get("text", ""):
                                                            font_size = span.get("size", 12)
                                                            break
                                    except:
                                        pass  # Use default font size
                                    
                                    # Insert new text
                                    page.insert_text(
                                        (inst.x0, inst.y0 + font_size),
                                        new_text,
                                        fontsize=font_size
                                    )
                                    print(f"    Inserted text at ({inst.x0:.1f}, {inst.y0 + font_size:.1f})")
                                except Exception as e:
                                    print(f"    Error inserting text: {e}")
                                    # Continue with other instances
                        else:
                            print(f"    Warning: Text '{old_text}' not found on page {page_num + 1}")
            
                # Save to bytes
                pdf_bytes = doc.tobytes()
                doc.close()
                print(f"PDF replacement complete, size: {len(pdf_bytes)} bytes")
                return pdf_bytes
            except Exception as e:
                print(f"PyMuPDF replacement failed: {e}")
                print("Falling back to PyPDF2")
                return self._replace_text_pypdf2(pdf_path, replacements)
        else:
            # Fallback to PyPDF2 if PyMuPDF not available
            print("PyMuPDF not available, using PyPDF2 fallback")
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

