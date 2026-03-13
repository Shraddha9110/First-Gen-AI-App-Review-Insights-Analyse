from fpdf import FPDF
import os

class ReportGenerator:
    def __init__(self):
        self.output_dir = "data/reports"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_pdf(self, data: dict, filename: str = "weekly_pulse.pdf") -> str:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Weekly Pulse: App Review Insights", ln=True, align='C')
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 10, "Generated via Gemini 2.0 Flash Analysis", ln=True, align='C')
        pdf.ln(10)

        # Summary
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 8, data.get("summary", "N/A"))
        pdf.ln(5)

        # Themes
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Top Themes", ln=True)
        pdf.set_font("Arial", '', 11)
        for theme in data.get("themes", []):
            pdf.cell(0, 8, f"- {theme}", ln=True)
        pdf.ln(5)

        # Quotes
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Real User Quotes", ln=True)
        pdf.set_font("Arial", 'I', 11)
        for quote in data.get("quotes", []):
            pdf.multi_cell(0, 8, f"\"{quote}\"")
            pdf.ln(2)
        pdf.ln(5)

        # Action Ideas
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Action Ideas", ln=True)
        pdf.set_font("Arial", '', 11)
        for action in data.get("actions", []):
            pdf.cell(0, 8, f"* {action}", ln=True)

        file_path = os.path.join(self.output_dir, filename)
        pdf.output(file_path)
        return file_path

    def generate_markdown(self, data: dict) -> str:
        md = f"""# Weekly Pulse: App Review Insights

## Executive Summary
{data.get('summary')}

## Top Themes
"""
        for theme in data.get('themes', []):
            md += f"- {theme}\n"
        
        md += "\n## Real User Quotes\n"
        for quote in data.get('quotes', []):
            md += f"> \"{quote}\"\n\n"
            
        md += "## Action Ideas\n"
        for action in data.get('actions', []):
            md += f"- {action}\n"
            
        return md
