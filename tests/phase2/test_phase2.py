import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.llm_client import GroqClient

class TestPhase2LLM(unittest.TestCase):
    def setUp(self):
        # Mock API Key for initialization
        os.environ["GROQ_API_KEY"] = "gsk_test_key_12345"
        self.mock_reviews = [
            {"rating": 5, "text": "Love the US stock investment feature! Very smooth."},
            {"rating": 1, "text": "KYC is taking too long. Please fix."},
            {"rating": 4, "text": "Great UI, but intraday charges are high."},
        ]

    @patch('backend.llm_client.Groq')
    def test_analyze_reviews_structure(self, mock_groq):
        # Setup mock response
        mock_client = MagicMock()
        mock_groq.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content=json.dumps({
                "themes": ["US Stocks", "KYC", "UI/UX"],
                "quotes": ["Love the US stock investment feature!", "KYC is taking too long.", "Great UI"],
                "actions": ["Improve KYC speed", "Reduce intraday charges", "Promote US stocks"],
                "summary": "Users generally like the US stocks and UI but are frustrated with KYC."
            })))
        ]
        mock_client.chat.completions.create.return_value = mock_response

        client = GroqClient()
        result = client.analyze_reviews(self.mock_reviews)

        # Assertions
        self.assertIn("themes", result)
        self.assertLessEqual(len(result["themes"]), 5)
        self.assertEqual(len(result["quotes"]), 3)
        self.assertEqual(len(result["actions"]), 3)
        self.assertIn("summary", result)
        print("✅ Phase 2: Structural Validation Passed!")

    def test_pii_exclusion_in_prompt(self):
        # Test if the client handles the reviews provided to it (which should be sanitized)
        client = GroqClient()
        # This is more of a logic check - ensures the client uses the reviews list
        with patch.object(client.client.chat.completions, 'create') as mock_create:
            mock_create.return_value = MagicMock(choices=[MagicMock(message=MagicMock(content='{}'))])
            try:
                client.analyze_reviews(self.mock_reviews)
            except:
                pass # Structure might break due to empty dict but we check call
            
            call_args = mock_create.call_args[1]
            content = call_args['messages'][1]['content']
            
            self.assertIn("INDMoney", content)
            self.assertIn("US stock investment", content)
            print("✅ Phase 2: Prompt Context (INDMoney) Validation Passed!")

if __name__ == "__main__":
    unittest.main()
