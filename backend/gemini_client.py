import os
import json
from typing import List, Dict
import requests

class GeminiClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY must be set")
        self.url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

    def analyze_reviews(self, reviews: List[Dict]) -> Dict:
        """
        Analyze reviews to extract themes, quotes, and action ideas for INDMoney.
        """
        formatted_reviews = "\n".join([
            f"Rating: {r.get('rating')} | Review: {r.get('text')}" 
            for r in reviews[:1000]
        ])

        prompt = f"""
        Analyze the following {len(reviews[:1000])} Play Store reviews for the app 'INDMoney' (a financial investment and tracking app) from the last 8-12 weeks. 
        Your goal is to generate a 'Weekly Pulse' report.
        
        Constraints:
        1. Max 5 themes.
        2. Exactly 3 key user quotes (representative of major themes).
        3. Exactly 3 action ideas.
        4. Total response MUST be scannable and ≤ 250 words.
        5. DO NOT include any usernames, emails, or PII.
        
        Reviews:
        {formatted_reviews}
        
        Return the result in the following JSON format:
        {{
            "themes": ["Theme 1", "Theme 2", ...],
            "quotes": ["Quote 1", "Quote 2", "Quote 3"],
            "actions": ["Action 1", "Action 2", "Action 3"],
            "summary": "Short 1-2 sentence overview"
        }}
        """

        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "responseMimeType": "application/json"
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }

        import time
        from .llm_client import GroqClient
        
        max_retries = 3
        last_status = None
        for attempt in range(max_retries):
            response = requests.post(f"{self.url}?key={self.api_key}", json=payload, headers=headers)
            last_status = response.status_code
            
            if response.status_code == 429:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 2 # Reduced wait for rapid fallback
                    print(f"⚠️ Gemini Rate limited (429). Retrying in {wait_time}s... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    print("🚨 Gemini limits exhausted. Falling back to Groq...")
                    try:
                        groq_llm = GroqClient()
                        return groq_llm.analyze_reviews(reviews)
                    except Exception as fallback_err:
                        return {
                            "themes": ["Fallback error"],
                            "quotes": ["Error switching to Groq"],
                            "actions": [f"Gemini 429 -> Groq Error: {str(fallback_err)}"],
                            "summary": f"Dual LLM failure: Gemini (429) and Groq ({str(fallback_err)})"
                        }
            break
        
        try:
            response.raise_for_status()
            data = response.json()
            # Extract text from Gemini response structure
            content = data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content)
        except Exception as e:
            # Final fallback if parsing or request fails
            return {
                "themes": ["Analysis error"],
                "quotes": ["Error calling Gemini API"],
                "actions": [f"Status code: {last_status if last_status else 'N/A'}"],
                "summary": f"Failed to get/parse LLM response: {str(e)}"
            }
