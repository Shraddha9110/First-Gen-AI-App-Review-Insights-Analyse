import os
from typing import List, Dict
from groq import Groq
import json

class GroqClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY must be set")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    def analyze_reviews(self, reviews: List[Dict]) -> Dict:
        """
        Analyze reviews to extract themes, quotes, and action ideas for INDMoney.
        """
        # Take up to 1000 reviews for comprehensive analysis
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

        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a product management assistant specializing in app review analysis. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=self.model,
            response_format={"type": "json_object"}
        )

        return json.loads(chat_completion.choices[0].message.content)
