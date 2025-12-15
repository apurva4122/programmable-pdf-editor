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
                    
                    # Get all text on page for debugging
                    page_text = page.get_text()
                    print(f"  Page text preview: {page_text[:200]}...")
                    
                    for old_text, new_text in replacements.items():
                        print(f"  Searching for: '{old_text}' -> '{new_text}'")
                        
                        # Try multiple search strategies
                        text_instances = []
                        
                        # Strategy 1: Exact match
                        text_instances = page.search_for(old_text)
                        print(f"    Exact match: Found {len(text_instances)} instances")
                        
                        # Strategy 2: Try with normalized whitespace
                        if not text_instances:
                            normalized_old = " ".join(old_text.split())
                            text_instances = page.search_for(normalized_old)
                            print(f"    Normalized whitespace: Found {len(text_instances)} instances")
                        
                        # Strategy 3: Try case-insensitive (if available)
                        if not text_instances:
                            try:
                                # Try uppercase version
                                text_instances = page.search_for(old_text.upper())
                                if not text_instances:
                                    text_instances = page.search_for(old_text.lower())
                                print(f"    Case-insensitive: Found {len(text_instances)} instances")
                            except:
                                pass
                        
                        # Strategy 4: Try partial match (first few words)
                        if not text_instances:
                            words = old_text.split()
                            if len(words) > 0:
                                partial = words[0] if len(words[0]) > 3 else " ".join(words[:2])
                                text_instances = page.search_for(partial)
                                print(f"    Partial match ('{partial}'): Found {len(text_instances)} instances")
                        
                        if text_instances:
                            print(f"  ✓ Found {len(text_instances)} instances to replace")
                            
                            # Get font info BEFORE redaction (while text still exists)
                            font_info_list = []
                            for inst in text_instances:
                                try:
                                    # Get text at this location to extract font info
                                    rect = fitz.Rect(inst)
                                    text_dict = page.get_text("dict")
                                    
                                    font_size = 12
                                    font_name = "helv"
                                    
                                    # Find font info for this text instance
                                    for block in text_dict.get("blocks", []):
                                        if "lines" in block:
                                            for line in block["lines"]:
                                                for span in line.get("spans", []):
                                                    span_bbox = span.get("bbox", [])
                                                    if len(span_bbox) == 4:
                                                        # Check if span overlaps with our rect
                                                        span_rect = fitz.Rect(span_bbox)
                                                        if rect.intersects(span_rect):
                                                            font_size = span.get("size", 12)
                                                            font_name = span.get("font", "helv")
                                                            break
                                    
                                    font_info_list.append({
                                        'rect': rect,
                                        'font_size': font_size,
                                        'font_name': font_name,
                                        'x0': inst.x0,
                                        'y0': inst.y0,
                                        'y1': inst.y1
                                    })
                                    print(f"    Instance font: size={font_size}, name={font_name}")
                                except Exception as e:
                                    print(f"    Could not get font info: {e}")
                                    font_info_list.append({
                                        'rect': fitz.Rect(inst),
                                        'font_size': 12,
                                        'font_name': 'helv',
                                        'x0': inst.x0,
                                        'y0': inst.y0,
                                        'y1': inst.y1
                                    })
                            
                            # Add redaction annotations
                            redaction_count = 0
                            for inst in text_instances:
                                try:
                                    page.add_redact_annot(inst)
                                    redaction_count += 1
                                except Exception as e:
                                    print(f"    Warning: Could not add redaction: {e}")
                            
                            print(f"  Added {redaction_count} redaction annotations")
                            
                            # Apply redactions (this removes the text)
                            try:
                                page.apply_redactions()
                                print(f"  ✓ Applied redactions")
                            except Exception as e:
                                print(f"    Error: Redaction failed: {e}")
                                import traceback
                                print(traceback.format_exc())
                            
                            # Insert new text at the redacted positions
                            for idx, font_info in enumerate(font_info_list):
                                try:
                                    # Calculate insertion point
                                    # PyMuPDF uses bottom-left as origin, so we need to position carefully
                                    # The y coordinate in PDFs increases from bottom to top
                                    # After redaction, we insert at the original position
                                    insert_x = font_info['x0']
                                    # Use y1 (bottom of text) as baseline for insertion
                                    # Adjust slightly to account for font descent
                                    insert_y = font_info['y1'] - (font_info['font_size'] * 0.2)  # Position near baseline
                                    
                                    # Try to insert text - use insertText which is more reliable
                                    try:
                                        # Method 1: Use insert_text (simpler)
                                        page.insert_text(
                                            (insert_x, insert_y),
                                            new_text,
                                            fontsize=font_info['font_size'],
                                            fontname=font_info['font_name'],
                                            color=(0, 0, 0)  # Black color
                                        )
                                        print(f"    ✓ Inserted '{new_text}' at ({insert_x:.1f}, {insert_y:.1f}) with font size {font_info['font_size']}, font '{font_info['font_name']}'")
                                    except Exception as insert_error:
                                        print(f"    insert_text failed: {insert_error}, trying alternative method")
                                        # Method 2: Use text insertion with TextWriter
                                        try:
                                            from fitz import TextWriter
                                            writer = TextWriter(page.rect)
                                            writer.append(
                                                (insert_x, insert_y),
                                                new_text,
                                                fontsize=font_info['font_size'],
                                                fontname=font_info['font_name']
                                            )
                                            writer.write_text(page)
                                            print(f"    ✓ Inserted '{new_text}' using TextWriter")
                                        except Exception as writer_error:
                                            print(f"    TextWriter also failed: {writer_error}")
                                            raise insert_error
                                except Exception as e:
                                    print(f"    ✗ Error inserting text for instance {idx + 1}: {e}")
                                    import traceback
                                    print(f"    Traceback: {traceback.format_exc()}")
                        else:
                            print(f"    ✗ Text '{old_text}' not found on page {page_num + 1}")
                            # Show what text is actually on the page for debugging
                            if old_text.lower() in page_text.lower():
                                print(f"    Note: Similar text found (case-insensitive match)")
                            # Check for partial matches
                            words = old_text.split()
                            found_words = [w for w in words if w.lower() in page_text.lower()]
                            if found_words:
                                print(f"    Note: Found words: {found_words}")
            
                # Save to bytes
                pdf_bytes = doc.tobytes()
                doc.close()
                print(f"PDF replacement complete, size: {len(pdf_bytes)} bytes")
                
                # Verify replacements were made by checking the output
                if pdf_bytes:
                    verify_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    verify_text = ""
                    for page in verify_doc:
                        verify_text += page.get_text()
                    verify_doc.close()
                    print(f"Verification: Output PDF contains {len(verify_text)} characters")
                    # Check if new text appears in output
                    for old_text, new_text in replacements.items():
                        if new_text in verify_text:
                            print(f"  ✓ Verified: '{new_text}' found in output PDF")
                        else:
                            print(f"  ⚠ Warning: '{new_text}' NOT found in output PDF")
                            # Check if old text still exists (replacement failed)
                            if old_text in verify_text:
                                print(f"  ⚠ Warning: Original text '{old_text}' still present (replacement may have failed)")
                
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

