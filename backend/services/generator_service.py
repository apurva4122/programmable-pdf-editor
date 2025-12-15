import random
from pathlib import Path
from typing import List, Dict
import zipfile
import asyncio
from services.pdf_service import PDFService

class GeneratorService:
    def __init__(self):
        self.pdf_service = PDFService()
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
    
    def _format_value(self, value: int, rule: Dict) -> str:
        """Format a numeric value according to rule"""
        # Apply format if specified
        if rule.get("format"):
            try:
                formatted = rule["format"] % value
            except:
                formatted = str(value)
        else:
            formatted = str(value)
        
        # Add prefix and suffix
        prefix = rule.get("prefix", "")
        suffix = rule.get("suffix", "")
        
        return f"{prefix}{formatted}{suffix}"
    
    def _generate_value(self, rule: Dict, copy_index: int) -> str:
        """Generate a value based on rule type"""
        rule_type = rule.get("type", "serial")
        
        if rule_type == "serial":
            start_value = rule.get("start_value", 1)
            value = start_value + copy_index
            return self._format_value(value, rule)
        
        elif rule_type == "random":
            min_val = rule.get("random_min", 1)
            max_val = rule.get("random_max", 100)
            value = random.randint(min_val, max_val)
            return self._format_value(value, rule)
        
        elif rule_type == "custom":
            # For custom, we might need more complex logic
            # For now, treat as serial
            start_value = rule.get("start_value", 1)
            value = start_value + copy_index
            return self._format_value(value, rule)
        
        return ""
    
    async def generate_pdfs(
        self,
        pdf_path: Path,
        rules: List[Dict],
        num_copies: int,
        ocr_sections: Optional[List[Dict]] = None
    ) -> List[Path]:
        """Generate multiple PDF copies with replacements"""
        output_files = []
        
        print(f"Generating {num_copies} copies with {len(rules)} rules")
        
        for copy_num in range(num_copies):
            try:
                print(f"Generating copy {copy_num + 1}/{num_copies}")
                replacements = {}
                
                # Generate replacement values for each rule
                for rule in rules:
                    original_text = rule.get("original_text", "")
                    new_value = self._generate_value(rule, copy_num)
                    
                    if original_text and new_value:
                        replacements[original_text] = new_value
                        print(f"  Rule: '{original_text}' -> '{new_value}'")
                
                if not replacements:
                    print(f"Warning: No replacements generated for copy {copy_num + 1}")
                
                # Build OCR coordinates map if available
                ocr_coords = None
                if ocr_sections:
                    ocr_coords = {}
                    for rule in rules:
                        original_text = rule.get("original_text", "")
                        section_id = rule.get("section_id", "")
                        # Find matching OCR section
                        for section in ocr_sections:
                            if section.get("id") == section_id or section.get("text", "").strip() == original_text.strip():
                                ocr_coords[original_text] = {
                                    "x": section.get("x", 0),
                                    "y": section.get("y", 0),
                                    "width": section.get("width", 100),
                                    "height": section.get("height", 20),
                                    "page": section.get("page", 0)
                                }
                                print(f"  Found OCR coordinates for '{original_text}': page {section.get('page', 0)}, ({section.get('x', 0)}, {section.get('y', 0)})")
                                break
                
                # Generate PDF with replacements
                print(f"  Replacing text in PDF...")
                pdf_bytes = self.pdf_service.replace_text_in_pdf(pdf_path, replacements, ocr_coords)
                
                # Save to file
                output_path = self.output_dir / f"{pdf_path.stem}_copy_{copy_num + 1}.pdf"
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)
                
                print(f"  Saved: {output_path}")
                output_files.append(output_path)
            except Exception as e:
                import traceback
                print(f"Error generating copy {copy_num + 1}: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                raise Exception(f"Failed to generate copy {copy_num + 1}: {str(e)}")
        
        print(f"Successfully generated {len(output_files)} PDF copies")
        return output_files
    
    async def create_zip(self, pdf_files: List[Path], pdf_id: str) -> Path:
        """Create a zip file containing all generated PDFs"""
        zip_path = self.output_dir / f"generated_{pdf_id}.zip"
        
        print(f"Creating ZIP file with {len(pdf_files)} PDFs")
        try:
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                for pdf_file in pdf_files:
                    if pdf_file.exists():
                        zipf.write(pdf_file, pdf_file.name)
                        print(f"  Added to ZIP: {pdf_file.name}")
                    else:
                        print(f"  Warning: File not found: {pdf_file}")
            
            print(f"ZIP file created: {zip_path} ({zip_path.stat().st_size} bytes)")
            return zip_path
        except Exception as e:
            import traceback
            print(f"Error creating ZIP file: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise

