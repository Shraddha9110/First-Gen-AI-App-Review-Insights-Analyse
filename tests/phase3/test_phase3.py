import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.gemini_client import GeminiClient

class TestPhase3Gemini(unittest.TestCase):
    def setUp(self):
        # Mock API Key for initialization
        os.environ["GEMINI_API_KEY"] = "fake_gemini_key_12345"
        self.mock_reviews = [
            {"rating": 5, "text": "Amazing UX!"},
            {"rating": 2, "text": "App crashes."},
        ]

    @patch('requests.post')
    def test_gemini_analyze_structure(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{
                        "text": json.dumps({
                            "themes": ["UX Quality", "Crash Issues"],
                            "quotes": ["Amazing UX", "App crashes"],
                            "actions": ["Fix bug", "Improve UI"],
                            "summary": "Mixed feedback."
                        })
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response

        client = GeminiClient()
        result = client.analyze_reviews(self.mock_reviews)

        # Assertions
        self.assertIn("themes", result)
        self.assertEqual(len(result["themes"]), 2)
        self.assertIn("summary", result)
        print("✅ Phase 3: Gemini (Requests) Structural Validation Passed!")

    def test_gemini_missing_key(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                GeminiClient(api_key=None)
        print("✅ Phase 3: Missing API Key Validation Passed!")

if __name__ == "__main__":
    unittest.main()
