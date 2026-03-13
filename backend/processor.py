import pandas as pd
import json
import re
from typing import List, Dict

class ReviewProcessor:
    @staticmethod
    def strip_pii(text: str) -> str:
        """Robust regex-based PII stripping."""
        if not isinstance(text, str):
            return ""
        # Strip emails
        text = re.sub(r'\S+@\S+', '[EMAIL]', text)
        # Strip common ID patterns or mentions
        text = re.sub(r'@\w+', '[USER]', text)
        # Strip potential transaction IDs or long numeric strings
        text = re.sub(r'\b\d{8,}\b', '[ID]', text)
        return text.strip()

    def process_csv(self, file_path: str, weeks: int = None) -> List[Dict]:
        df = pd.read_csv(file_path)
        return self._process_dataframe(df, weeks=weeks)

    def process_json(self, file_path: str, weeks: int = None) -> List[Dict]:
        with open(file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return self._process_dataframe(df, weeks=weeks)

    def _process_dataframe(self, df: pd.DataFrame, weeks: int = None) -> List[Dict]:
        # Required columns: rating, title, text, date
        # Normalizing column names to lowercase
        df.columns = [c.lower() for c in df.columns]
        
        required = ['rating', 'text'] 
        for col in required:
            if col not in df.columns:
                if col == 'text' and 'content' in df.columns:
                    df['text'] = df['content']
                elif col == 'text' and 'review' in df.columns:
                    df['text'] = df['review']
                else:
                    raise ValueError(f"Missing required column: {col}")

        # Basic cleaning
        df['text'] = df['text'].apply(self.strip_pii)
        
        # Date filtering logic
        if 'date' in df.columns and weeks is not None:
            try:
                df['date'] = pd.to_datetime(df['date'])
                cutoff = pd.Timestamp.now() - pd.Timedelta(weeks=weeks)
                df = df[df['date'] >= cutoff]
            except Exception as e:
                print(f"⚠️ Warning: Could not filter by date: {e}")
        
        return df[['rating', 'text']].to_dict('records')
