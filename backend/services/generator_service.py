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
        num_copies: int
    ) -> List[Path]:
        """Generate multiple PDF copies with replacements"""
        output_files = []
        
        # Read original PDF sections (we'll need to store original text)
        # For now, we'll use the section_id to identify what to replace
        
        for copy_num in range(num_copies):
            replacements = {}
            
            # Generate replacement values for each rule
            for rule in rules:
                original_text = rule.get("original_text", "")
                new_value = self._generate_value(rule, copy_num)
                
                if original_text and new_value:
                    replacements[original_text] = new_value
            
            # Generate PDF with replacements
            pdf_bytes = self.pdf_service.replace_text_in_pdf(pdf_path, replacements)
            
            # Save to file
            output_path = self.output_dir / f"{pdf_path.stem}_copy_{copy_num + 1}.pdf"
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)
            
            output_files.append(output_path)
        
        return output_files
    
    async def create_zip(self, pdf_files: List[Path], pdf_id: str) -> Path:
        """Create a zip file containing all generated PDFs"""
        zip_path = self.output_dir / f"generated_{pdf_id}.zip"
        
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for pdf_file in pdf_files:
                zipf.write(pdf_file, pdf_file.name)
        
        return zip_path

