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
                                # OCR coordinates are in pixels from top-left (from image)
                                # PDF coordinates are in points (72 DPI) from bottom-left
                                try:
                                    ocr_x = coord_info.get("x", 0)
                                    ocr_y = coord_info.get("y", 0)
                                    ocr_width = coord_info.get("width", 100)
                                    ocr_height = coord_info.get("height", 20)
                                    
                                    # Get page dimensions in PDF points
                                    page_rect = page.rect
                                    page_width_pt = page_rect.width
                                    page_height_pt = page_rect.height
                                    
                                    # pdf2image converts PDF to images at 200 DPI by default
                                    # Scale factor: PDF points = OCR pixels * (72 / 200) = OCR pixels * 0.36
                                    ocr_dpi = 200  # DPI used by pdf2image (from ocr_service.py)
                                    scale_factor = 72.0 / ocr_dpi  # Convert pixels to points (0.36)
                                    
                                    # Scale OCR coordinates from pixels to PDF points
                                    pdf_x0 = ocr_x * scale_factor
                                    pdf_width = ocr_width * scale_factor
                                    pdf_height = ocr_height * scale_factor
                                    
                                    # OCR Y coordinate conversion:
                                    # OCR uses top-left origin (y=0 at top, increases downward)
                                    # PDF uses bottom-left origin (y=0 at bottom, increases upward)
                                    # 
                                    # OCR bounding box:
                                    #   - Top edge: ocr_y (in pixels, measured from top of image)
                                    #   - Bottom edge: ocr_y + ocr_height (in pixels, measured from top of image)
                                    #
                                    # Step 1: Scale OCR pixels to PDF points
                                    ocr_y_top_pt = ocr_y * scale_factor  # Top edge in PDF points (still measured from top)
                                    ocr_y_bottom_pt = (ocr_y + ocr_height) * scale_factor  # Bottom edge in PDF points (still measured from top)
                                    
                                    # Step 2: Convert from top-left origin to bottom-left origin
                                    # In PDF: y=0 is at bottom, y=page_height is at top
                                    # OCR: y=0 at top, increases downward
                                    # PDF: y=0 at bottom, increases upward
                                    # So: pdf_y = page_height - ocr_y_scaled
                                    # 
                                    # IMPORTANT: We need to flip BOTH top and bottom
                                    # OCR top (smaller y in OCR) -> PDF bottom (smaller y in PDF)
                                    # OCR bottom (larger y in OCR) -> PDF top (larger y in PDF)
                                    pdf_y0 = page_height_pt - ocr_y_bottom_pt  # Bottom of text box in PDF (was OCR bottom)
                                    pdf_y1 = page_height_pt - ocr_y_top_pt  # Top of text box in PDF (was OCR top)
                                    
                                    pdf_x1 = pdf_x0 + pdf_width
                                    
                                    print(f"    Y coordinate conversion:")
                                    print(f"      OCR top: {ocr_y}px -> {ocr_y_top_pt:.2f}pt (from top)")
                                    print(f"      OCR bottom: {ocr_y + ocr_height}px -> {ocr_y_bottom_pt:.2f}pt (from top)")
                                    print(f"      PDF y1 (top): {page_height_pt:.2f} - {ocr_y_top_pt:.2f} = {pdf_y1:.2f}")
                                    print(f"      PDF y0 (bottom): {page_height_pt:.2f} - {ocr_y_bottom_pt:.2f} = {pdf_y0:.2f}")
                                    
                                    # Ensure coordinates are within page bounds
                                    pdf_x0 = max(0, min(pdf_x0, page_width_pt))
                                    pdf_x1 = max(0, min(pdf_x1, page_width_pt))
                                    pdf_y0 = max(0, min(pdf_y0, page_height_pt))
                                    pdf_y1 = max(0, min(pdf_y1, page_height_pt))
                                    
                                    text_rect = fitz.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
                                    text_instances = [text_rect]
                                    print(f"    ✓ Using OCR coordinates:")
                                    print(f"      OCR pixels: x={ocr_x}, y={ocr_y}, w={ocr_width}, h={ocr_height}")
                                    print(f"      Scale factor (72/200): {scale_factor:.4f}")
                                    print(f"      PDF points: ({pdf_x0:.1f}, {pdf_y0:.1f}) to ({pdf_x1:.1f}, {pdf_y1:.1f})")
                                    print(f"      Page size: {page_width_pt:.1f}x{page_height_pt:.1f} points")
                                except Exception as coord_error:
                                    print(f"    Error converting OCR coordinates: {coord_error}")
                                    import traceback
                                    print(traceback.format_exc())
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
                                    best_match_area = 0
                                    best_match_span = None
                                    
                                    # Find font info for this text instance
                                    # Look for spans that overlap with our rect
                                    for block in text_dict.get("blocks", []):
                                        if "lines" in block:
                                            for line in block["lines"]:
                                                for span in line.get("spans", []):
                                                    span_bbox = span.get("bbox", [])
                                                    if len(span_bbox) == 4:
                                                        span_rect = fitz.Rect(span_bbox)
                                                        # Check if span overlaps with our rect
                                                        if rect.intersects(span_rect):
                                                            # Calculate overlap area to find best match
                                                            overlap = rect & span_rect
                                                            overlap_area = overlap.width * overlap.height if overlap.is_valid else 0
                                                            
                                                            if overlap_area > best_match_area:
                                                                best_match_area = overlap_area
                                                                best_match_span = span
                                    
                                    # Use the best matching span's font info
                                    if best_match_span:
                                        font_size = best_match_span.get("size", 12)
                                        font_name = best_match_span.get("font", "helv")
                                        print(f"    Found font match: size={font_size:.1f}, name={font_name}, overlap_area={best_match_area:.1f}")
                                    else:
                                        # If no match found, try to estimate from rect height
                                        # Font size is typically about 70-80% of the text box height
                                        # Account for line spacing, ascenders, and descenders
                                        rect_height = rect.height
                                        
                                        # Try to find any text near this location for font size reference
                                        nearby_font_size = None
                                        for block in text_dict.get("blocks", []):
                                            if "lines" in block:
                                                for line in block["lines"]:
                                                    for span in line.get("spans", []):
                                                        span_bbox = span.get("bbox", [])
                                                        if len(span_bbox) == 4:
                                                            span_rect = fitz.Rect(span_bbox)
                                                            # Check if span is near our rect (within 20 points horizontally)
                                                            center_dist_x = abs((span_rect.x0 + span_rect.x1)/2 - (rect.x0 + rect.x1)/2)
                                                            center_dist_y = abs((span_rect.y0 + span_rect.y1)/2 - (rect.y0 + rect.y1)/2)
                                                            if center_dist_x < 20 and center_dist_y < 50:
                                                                nearby_font_size = span.get("size", None)
                                                                font_name = span.get("font", "helv")
                                                                if nearby_font_size:
                                                                    print(f"    Found nearby font: size={nearby_font_size:.1f}, name={font_name}")
                                                                    break
                                                    if nearby_font_size:
                                                        break
                                            if nearby_font_size:
                                                break
                                        
                                        if nearby_font_size:
                                            font_size = nearby_font_size
                                        else:
                                            # Estimate from rect height - be more conservative
                                            # Text box height includes ascenders/descenders, so font is smaller
                                            estimated_size = rect_height * 0.75  # More conservative estimate
                                            
                                            # Round to nearest reasonable value instead of rejecting
                                            if estimated_size < 6:
                                                font_size = 6  # Minimum reasonable font size
                                                print(f"    Estimated size {estimated_size:.1f} too small, using minimum: {font_size}")
                                            elif estimated_size > 72:
                                                font_size = 72  # Maximum reasonable font size
                                                print(f"    Estimated size {estimated_size:.1f} too large, using maximum: {font_size}")
                                            else:
                                                # Round to nearest 0.5 for cleaner values
                                                font_size = round(estimated_size * 2) / 2
                                                print(f"    Estimated font size from rect height: {font_size:.1f} (rect height: {rect_height:.1f}, raw estimate: {estimated_size:.1f})")
                                    
                                    font_info_list.append({
                                        'rect': rect,
                                        'font_size': font_size,
                                        'font_name': font_name,
                                        'x0': inst.x0,
                                        'y0': inst.y0,
                                        'y1': inst.y1
                                    })
                                    print(f"    Final font info: size={font_size:.1f}, name={font_name}")
                                except Exception as e:
                                    print(f"    Could not get font info: {e}")
                                    import traceback
                                    print(traceback.format_exc())
                                    # Estimate from rect if available
                                    estimated_size = (inst.y1 - inst.y0) * 0.75 if hasattr(inst, 'y1') and hasattr(inst, 'y0') else 12
                                    # Round to nearest reasonable value
                                    if estimated_size < 6:
                                        final_size = 6
                                    elif estimated_size > 72:
                                        final_size = 72
                                    else:
                                        final_size = round(estimated_size * 2) / 2  # Round to nearest 0.5
                                    
                                    font_info_list.append({
                                        'rect': fitz.Rect(inst),
                                        'font_size': final_size,
                                        'font_name': 'helv',
                                        'x0': inst.x0,
                                        'y0': inst.y0,
                                        'y1': inst.y1
                                    })
                                    print(f"    Fallback font size: {final_size:.1f} (estimated: {estimated_size:.1f})")
                            
                            # Add redaction annotations and apply them
                            redaction_count = 0
                            for inst in text_instances:
                                try:
                                    # Create redaction annotation
                                    redact_annot = page.add_redact_annot(inst)
                                    # Fill with white color to hide the text
                                    redact_annot.set_colors(stroke=(1, 1, 1), fill=(1, 1, 1))  # White
                                    redact_annot.update()
                                    redaction_count += 1
                                    print(f"    Added redaction annotation at ({inst.x0:.1f}, {inst.y0:.1f}) to ({inst.x1:.1f}, {inst.y1:.1f})")
                                except Exception as e:
                                    print(f"    Warning: Could not add redaction: {e}")
                                    import traceback
                                    print(traceback.format_exc())
                            
                            print(f"  Added {redaction_count} redaction annotations")
                            
                            # Apply redactions (this removes the text)
                            try:
                                # First, try to apply redactions normally
                                page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
                                print(f"  ✓ Applied redactions")
                                
                                # Verify text was removed
                                page_text_after = page.get_text()
                                if old_text in page_text_after:
                                    print(f"  ⚠ Warning: Text '{old_text}' still present after redaction!")
                                    print(f"  Attempting alternative: drawing white rectangles...")
                                    # If redaction didn't work, draw white rectangles to cover the text
                                    for inst in text_instances:
                                        rect = fitz.Rect(inst)
                                        # Draw white filled rectangle to cover the text
                                        shape = page.new_shape()
                                        shape.draw_rect(rect)
                                        shape.finish(fill=(1, 1, 1), color=(1, 1, 1))  # White fill and stroke
                                        shape.commit()
                                    print(f"  ✓ Drew white rectangles to cover text")
                                else:
                                    print(f"  ✓ Verified: Text '{old_text}' removed successfully")
                            except Exception as e:
                                print(f"    Error: Redaction failed: {e}")
                                import traceback
                                print(traceback.format_exc())
                                # Fallback: manually draw white rectangles
                                try:
                                    print(f"    Attempting manual text removal with white rectangles...")
                                    for inst in text_instances:
                                        rect = fitz.Rect(inst)
                                        # Use shape to draw white rectangle
                                        shape = page.new_shape()
                                        shape.draw_rect(rect)
                                        shape.finish(fill=(1, 1, 1), color=(1, 1, 1))
                                        shape.commit()
                                    print(f"    ✓ Drew white rectangles to cover text (fallback)")
                                except Exception as manual_error:
                                    print(f"    Manual removal also failed: {manual_error}")
                                    import traceback
                                    print(traceback.format_exc())
                            
                            # Insert new text at the redacted positions
                            # IMPORTANT: After apply_redactions(), we need to insert text as new content
                            for idx, font_info in enumerate(font_info_list):
                                try:
                                    # Calculate insertion point
                                    # PyMuPDF coordinate system: origin at bottom-left
                                    # The rect: x0=left, y0=bottom, x1=right, y1=top
                                    # For text insertion, we need the baseline position
                                    
                                    insert_x = font_info['x0']
                                    # Position text at baseline
                                    # In PDF, text is positioned at the baseline
                                    # y0 is the bottom of the text bounding box
                                    # The baseline is typically at y0 + a small offset for descenders
                                    # For most fonts, descenders are about 20-25% of font size
                                    # But we want the text to align with the original, so use y0 directly or small offset
                                    baseline_offset = font_info['font_size'] * 0.15  # Smaller offset
                                    insert_y = font_info['y0'] + baseline_offset
                                    
                                    print(f"    Inserting '{new_text}' at ({insert_x:.2f}, {insert_y:.2f})")
                                    print(f"    Original rect: x0={font_info['x0']:.2f}, y0={font_info['y0']:.2f}, y1={font_info['y1']:.2f}, height={font_info['y1']-font_info['y0']:.2f}")
                                    print(f"    Font: size={font_info['font_size']:.2f}, name={font_info['font_name']}, baseline_offset={baseline_offset:.2f}")
                                    
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

