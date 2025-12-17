from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional

try:
    import fitz  # PyMuPDF for better text replacement
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

class PDFService:
    def __init__(self):
        pass
    
    def replace_text_in_pdf(self, pdf_path: Path, replacements: Dict[str, str], ocr_coordinates: Optional[Dict[str, Dict]] = None) -> bytes:
        """
        Replace text in PDF using PyMuPDF for better text replacement
        replacements: dict mapping original text to new text
        ocr_coordinates: optional dict mapping original_text to OCR bounding box coordinates
                         Format: {"text": {"x": x, "y": y, "width": w, "height": h, "page": page_num}}
        """
        if not replacements:
            print("Warning: No replacements provided, returning original PDF")
            with open(pdf_path, "rb") as f:
                return f.read()
        
        print(f"Replacing {len(replacements)} text strings in PDF")
        if ocr_coordinates:
            print(f"Using OCR coordinates for {len(ocr_coordinates)} text items")
        
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
                        print(f"  Text length: {len(old_text)} characters")
                        
                        # Check if we have OCR coordinates for this text
                        text_instances = []
                        if ocr_coordinates and old_text in ocr_coordinates:
                            coord_info = ocr_coordinates[old_text]
                            if coord_info.get("page") == page_num:
                                # Convert OCR coordinates to PDF coordinates
                                # OCR coordinates are typically in pixels from top-left
                                # PDF coordinates are in points (72 DPI) from bottom-left
                                try:
                                    ocr_x = coord_info.get("x", 0)
                                    ocr_y = coord_info.get("y", 0)
                                    ocr_width = coord_info.get("width", 100)
                                    ocr_height = coord_info.get("height", 20)
                                    
                                    # Get page dimensions
                                    page_rect = page.rect
                                    page_height = page_rect.height
                                    
                                    # Convert OCR coordinates (top-left origin) to PDF coordinates (bottom-left origin)
                                    # Assuming OCR image is same size as PDF page
                                    pdf_x0 = ocr_x
                                    pdf_y0 = page_height - (ocr_y + ocr_height)  # Flip Y coordinate
                                    pdf_x1 = ocr_x + ocr_width
                                    pdf_y1 = page_height - ocr_y
                                    
                                    text_rect = fitz.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
                                    text_instances = [text_rect]
                                    print(f"    ✓ Using OCR coordinates: ({pdf_x0:.1f}, {pdf_y0:.1f}) to ({pdf_x1:.1f}, {pdf_y1:.1f})")
                                except Exception as coord_error:
                                    print(f"    Error converting OCR coordinates: {coord_error}")
                                    text_instances = []
                        
                        # If OCR coordinates didn't work, try text search
                        if not text_instances:
                            # Get all text from PDF for comparison
                            pdf_text_raw = page.get_text()
                            pdf_text_normalized = " ".join(pdf_text_raw.split())
                            print(f"  PDF page text preview (first 300 chars): {pdf_text_raw[:300]}")
                            print(f"  PDF normalized text preview: {pdf_text_normalized[:300]}")
                            
                            # Try multiple search strategies
                            
                            # Strategy 1: Exact match
                            text_instances = page.search_for(old_text)
                            print(f"    Strategy 1 - Exact match: Found {len(text_instances)} instances")
                            
                            # Strategy 2: Try with normalized whitespace (remove extra spaces/newlines)
                            if not text_instances:
                                normalized_old = " ".join(old_text.split())
                                text_instances = page.search_for(normalized_old)
                                print(f"    Strategy 2 - Normalized whitespace ('{normalized_old}'): Found {len(text_instances)} instances")
                            
                            # Strategy 3: Try removing all whitespace
                            if not text_instances:
                                no_space_old = old_text.replace(" ", "").replace("\n", "").replace("\t", "")
                                no_space_pdf = pdf_text_raw.replace(" ", "").replace("\n", "").replace("\t", "")
                                if no_space_old in no_space_pdf:
                                    # Found without spaces, now try to find with minimal spaces
                                    # Try each word separately and find overlapping regions
                                    words = old_text.split()
                                    if len(words) > 0:
                                        # Try searching for first word, then check if subsequent words are nearby
                                        first_word_instances = page.search_for(words[0])
                                        if first_word_instances:
                                            print(f"    Strategy 3 - Found first word '{words[0]}' {len(first_word_instances)} times")
                                            # For now, use first word instances as approximation
                                            text_instances = first_word_instances[:1]  # Take first instance
                                            print(f"    Using first word as approximation")
                            
                            # Strategy 4: Try case-insensitive variations
                            if not text_instances:
                                try:
                                    text_instances = page.search_for(old_text.upper())
                                    if not text_instances:
                                        text_instances = page.search_for(old_text.lower())
                                    if not text_instances:
                                        text_instances = page.search_for(old_text.capitalize())
                                    print(f"    Strategy 4 - Case-insensitive: Found {len(text_instances)} instances")
                                except:
                                    pass
                            
                            # Strategy 5: Try partial match (first few words or longest word)
                            if not text_instances:
                                words = old_text.split()
                                if len(words) > 0:
                                    # Try longest word (likely most unique)
                                    longest_word = max(words, key=len)
                                    if len(longest_word) > 3:
                                        text_instances = page.search_for(longest_word)
                                        print(f"    Strategy 5 - Longest word ('{longest_word}'): Found {len(text_instances)} instances")
                                    
                                    # If still not found, try first word
                                    if not text_instances and len(words[0]) > 2:
                                        text_instances = page.search_for(words[0])
                                        print(f"    Strategy 5 - First word ('{words[0]}'): Found {len(text_instances)} instances")
                            
                            # Strategy 6: Try searching for individual characters/numbers (for invoice numbers, etc.)
                            if not text_instances:
                                # If text looks like a number or code, try searching for it as-is
                                if old_text.strip().isdigit() or any(c.isdigit() for c in old_text):
                                    # Try with and without spaces around numbers
                                    for variant in [old_text.strip(), old_text.replace(" ", ""), old_text.replace("-", "")]:
                                        text_instances = page.search_for(variant)
                                        if text_instances:
                                            print(f"    Strategy 6 - Number variant ('{variant}'): Found {len(text_instances)} instances")
                                            break
                            
                            # Strategy 7: Fuzzy match - check if text exists in page text (case-insensitive)
                            if not text_instances:
                                old_lower = old_text.lower().strip()
                                pdf_lower = pdf_text_raw.lower()
                                if old_lower in pdf_lower:
                                    print(f"    Strategy 7 - Text found in page text (case-insensitive) but search_for failed")
                                    print(f"    This suggests a formatting/encoding mismatch")
                                    # Try to extract position from text blocks
                                    try:
                                        text_dict = page.get_text("dict")
                                        for block in text_dict.get("blocks", []):
                                            if "lines" in block:
                                                for line in block["lines"]:
                                                    line_text = "".join([span.get("text", "") for span in line.get("spans", [])])
                                                    if old_lower in line_text.lower():
                                                        # Found matching line, get its bbox
                                                        bbox = line.get("bbox", [])
                                                        if len(bbox) == 4:
                                                            text_instances = [fitz.Rect(bbox)]
                                                            print(f"    Strategy 7 - Found via text dict bbox: {bbox}")
                                                            break
                                                    if text_instances:
                                                        break
                                            if text_instances:
                                                break
                                    except Exception as e:
                                        print(f"    Strategy 7 - Error extracting bbox: {e}")
                        
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
                            # IMPORTANT: After apply_redactions(), we need to insert text as new content
                            for idx, font_info in enumerate(font_info_list):
                                try:
                                    # Calculate insertion point
                                    # PyMuPDF coordinate system: origin at bottom-left
                                    # y1 is the bottom of the text box, y0 is the top
                                    insert_x = font_info['x0']
                                    # Position text at baseline (slightly above y1 to account for font descent)
                                    # Most fonts have about 20% descent, so we position slightly above y1
                                    insert_y = font_info['y1'] - (font_info['font_size'] * 0.15)
                                    
                                    print(f"    Attempting to insert '{new_text}' at ({insert_x:.2f}, {insert_y:.2f})")
                                    print(f"    Original rect: x0={font_info['x0']:.2f}, y0={font_info['y0']:.2f}, y1={font_info['y1']:.2f}")
                                    
                                    # Method 1: Use insert_text with explicit rendering
                                    try:
                                        # Insert text directly
                                        rc = page.insert_text(
                                            (insert_x, insert_y),
                                            new_text,
                                            fontsize=font_info['font_size'],
                                            fontname=font_info['font_name'],
                                            color=(0, 0, 0),  # Black color
                                            render_mode=0  # Fill text
                                        )
                                        print(f"    ✓ insert_text returned: {rc}")
                                        print(f"    ✓ Inserted '{new_text}' at ({insert_x:.1f}, {insert_y:.1f}) with font size {font_info['font_size']}, font '{font_info['font_name']}'")
                                    except Exception as insert_error:
                                        print(f"    insert_text failed: {insert_error}")
                                        # Method 2: Try using TextWriter (more control)
                                        try:
                                            from fitz import TextWriter
                                            tw = TextWriter(page.rect)
                                            tw.append(
                                                (insert_x, insert_y),
                                                new_text,
                                                fontsize=font_info['font_size'],
                                                fontname=font_info['font_name']
                                            )
                                            tw.write_text(page)
                                            print(f"    ✓ Inserted '{new_text}' using TextWriter")
                                        except Exception as writer_error:
                                            print(f"    TextWriter failed: {writer_error}")
                                            # Method 3: Try inserting as annotation (last resort)
                                            try:
                                                annot = page.add_freetext_annot(
                                                    fitz.Rect(insert_x, insert_y - font_info['font_size'], 
                                                             insert_x + len(new_text) * font_info['font_size'] * 0.6, 
                                                             insert_y),
                                                    new_text,
                                                    fontsize=font_info['font_size'],
                                                    fontname=font_info['font_name']
                                                )
                                                annot.update()
                                                print(f"    ✓ Inserted '{new_text}' as annotation")
                                            except Exception as annot_error:
                                                print(f"    All insertion methods failed. Last error: {annot_error}")
                                                raise insert_error
                                except Exception as e:
                                    print(f"    ✗ Error inserting text for instance {idx + 1}: {e}")
                                    import traceback
                                    print(f"    Traceback: {traceback.format_exc()}")
                        else:
                            print(f"    ✗ Text '{old_text}' not found on page {page_num + 1}")
                            print(f"    ===== DEBUGGING INFO =====")
                            print(f"    Original text to find: '{old_text}'")
                            print(f"    Text length: {len(old_text)}")
                            print(f"    PDF page text length: {len(pdf_text_raw)}")
                            
                            # Show what text is actually on the page for debugging
                            old_lower = old_text.lower().strip()
                            pdf_lower = pdf_text_raw.lower()
                            
                            if old_lower in pdf_lower:
                                print(f"    ✓ Text EXISTS in page (case-insensitive match)")
                                print(f"    This means search_for() failed due to formatting differences")
                                # Try to find the position manually
                                idx = pdf_lower.find(old_lower)
                                print(f"    Found at character position {idx} in page text")
                                
                                # Try to get text blocks and find matching one
                                try:
                                    text_dict = page.get_text("dict")
                                    print(f"    Attempting to find text via text blocks...")
                                    for block_idx, block in enumerate(text_dict.get("blocks", [])):
                                        if "lines" in block:
                                            for line_idx, line in enumerate(block["lines"]):
                                                line_text_parts = []
                                                for span in line.get("spans", []):
                                                    span_text = span.get("text", "")
                                                    line_text_parts.append(span_text)
                                                line_text = "".join(line_text_parts)
                                                
                                                if old_lower in line_text.lower():
                                                    bbox = line.get("bbox", [])
                                                    if len(bbox) == 4:
                                                        print(f"    Found matching line in block {block_idx}, line {line_idx}")
                                                        print(f"    Line text: '{line_text[:100]}'")
                                                        print(f"    Line bbox: {bbox}")
                                                        # Use this bbox as the replacement area
                                                        text_instances = [fitz.Rect(bbox)]
                                                        print(f"    ✓ Created rect from text block bbox")
                                                        break
                                                if text_instances:
                                                    break
                                        if text_instances:
                                            break
                                except Exception as e:
                                    print(f"    Error in text block search: {e}")
                                    import traceback
                                    print(traceback.format_exc())
                            else:
                                print(f"    ✗ Text does NOT exist in page (even case-insensitive)")
                                # Check for partial matches
                                words = old_text.split()
                                found_words = [w for w in words if w.lower() in pdf_lower and len(w) > 2]
                                if found_words:
                                    print(f"    Note: Some words found: {found_words}")
                                else:
                                    print(f"    Note: No matching words found")
                                    
                                # Show similar text snippets
                                print(f"    Showing similar text snippets from PDF:")
                                for word in words[:3]:  # Check first 3 words
                                    if len(word) > 3:
                                        # Find this word in PDF and show context
                                        word_lower = word.lower()
                                        if word_lower in pdf_lower:
                                            idx = pdf_lower.find(word_lower)
                                            context = pdf_text_raw[max(0, idx-50):min(len(pdf_text_raw), idx+len(word)+50)]
                                            print(f"      Found '{word}' in context: ...{context}...")
                            
                            print(f"    ===== END DEBUGGING =====")
                            
                            # If we still don't have instances, skip this replacement
                            if not text_instances:
                                print(f"    ⚠ SKIPPING replacement for '{old_text}' - text not found")
                                continue
            
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

