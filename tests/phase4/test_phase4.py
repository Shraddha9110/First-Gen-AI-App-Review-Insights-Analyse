import sys
import os
import unittest
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.report_generator import ReportGenerator

class TestPhase4Reporting(unittest.TestCase):
    def setUp(self):
        self.report_gen = ReportGenerator()
        self.test_data = {
            "summary": "This is a test summary for the PDF report.",
            "themes": ["Theme A", "Theme B"],
            "quotes": ["Test quote 1", "Test quote 2"],
            "actions": ["Action X", "Action Y"]
        }

    def test_pdf_generation(self):
        filename = "test_pulse_report.pdf"
        file_path = self.report_gen.generate_pdf(self.test_data, filename=filename)
        
        # Check if file exists
        self.assertTrue(os.path.exists(file_path))
        # Check if file is not empty
        self.assertGreater(os.path.getsize(file_path), 0)
        
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        print("✅ Phase 4: PDF Generation Validation Passed!")

    def test_markdown_generation(self):
        md_content = self.report_gen.generate_markdown(self.test_data)
        self.assertIn("# Weekly Pulse", md_content)
        self.assertIn("## Executive Summary", md_content)
        self.assertIn("Theme A", md_content)
        self.assertIn("Test quote 1", md_content)
        print("✅ Phase 4: Markdown Generation Validation Passed!")

if __name__ == "__main__":
    unittest.main()
