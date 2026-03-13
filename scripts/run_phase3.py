import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.processor import ReviewProcessor
from backend.gemini_client import GeminiClient

def main():
    # Load environment variables from .env
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment or .env file.")
        print("Please add 'GEMINI_API_KEY=your_key_here' to the .env file.")
        return

    csv_path = "data/sample_reviews.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found.")
        return

    print(f"🔄 Processing reviews from {csv_path} for Phase 3 (Gemini)...")
    processor = ReviewProcessor()
    try:
        reviews = processor.process_csv(csv_path)
    except Exception as e:
        print(f"❌ Error processing CSV: {e}")
        return

    print(f"✅ Loaded {len(reviews)} reviews.")
    print("🚀 Sending to Google Gemini LLM for analysis (Gemini 2.0 Flash)...")

    llm = GeminiClient(api_key=api_key)
    try:
        results = llm.analyze_reviews(reviews)
        
        print("\n" + "="*50)
        print("📊 PHASE 3: GEMINI WEEKLY PULSE REPORT")
        print("="*50)
        print(f"\n📝 Summary: {results.get('summary')}")
        
        print("\n🔥 Top Themes:")
        for theme in results.get('themes', []):
            print(f"  • {theme}")
            
        print("\n💬 Key User Quotes:")
        for quote in results.get('quotes', []):
            print(f"  \" {quote} \"")
            
        print("\n💡 Action Ideas:")
        for action in results.get('actions', []):
            print(f"  → {action}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error during Gemini analysis: {e}")

if __name__ == "__main__":
    main()
