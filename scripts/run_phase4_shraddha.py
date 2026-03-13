import os
import sys
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.processor import ReviewProcessor
from backend.gemini_client import GeminiClient
from backend.report_generator import ReportGenerator

def main():
    load_dotenv()
    
    recipient_name = "Shraddha"
    recipient_email = "Shraddha.jagtap5050@gmail.com"
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        return

    csv_path = "data/sample_reviews.csv"
    processor = ReviewProcessor()
    reviews = processor.process_csv(csv_path)

    print(f"🚀 Running Phase 4 for {recipient_name} ({recipient_email})...")
    
    llm = GeminiClient(api_key=api_key)
    try:
        results = llm.analyze_reviews(reviews)
        
        # Add recipient info for reporting
        results['recipient_name'] = recipient_name
        results['recipient_email'] = recipient_email
        
        report_gen = ReportGenerator()
        
        # 1. Generate PDF
        pdf_filename = f"INDMoney_Pulse_{recipient_name}.pdf"
        pdf_path = report_gen.generate_pdf(results, filename=pdf_filename)
        print(f"✅ PDF Report generated: {pdf_path}")
        
        # 2. Generate Personalized Email Body
        themes_str = "\n".join([f"{i+1}. {t}" for i, t in enumerate(results.get('themes', []))])
        quotes_str = "\n".join([f"{i+1}. \"{q}\"" for i, q in enumerate(results.get('quotes', []))])
        actions_str = "\n".join([f"{i+1}. {a}" for i, a in enumerate(results.get('actions', []))])

        email_body = f"""Subject: INDmoney weekly review pulse - week of March 12, 2026

Hi {recipient_name},

Here is your personalized weekly pulse for INDMoney based on the latest 200 reviews.

EXECUTIVE SUMMARY
{results.get('summary')}

TOP THEMES
{themes_str}

REAL USER QUOTES
{quotes_str}

ACTION IDEAS
{actions_str}

Best Regards,
INDMoney Product Insights Bot
"""
        
        output_dir = "pulse"
        os.makedirs(output_dir, exist_ok=True)
        email_path = os.path.join(output_dir, f"email_for_{recipient_name}.md")
        
        with open(email_path, 'w') as f:
            f.write(email_body)
            
        print(f"✅ Personalized Email Body saved: {email_path}")
        
        # 3. Trigger Backend Email
        print(f"📧 Prompting backend to send email to {recipient_email}...")
        import requests
        email_payload = {
            "name": recipient_name,
            "email": recipient_email,
            "analysis": results
        }
        email_response = requests.post("http://127.0.0.1:8000/send-email", json=email_payload)
        
        if email_response.status_code == 200:
            print(f"🚀 SUCCESS: Personalized email sent to {recipient_email}")
        else:
            print(f"❌ FAILED: Backend returned {email_response.status_code}: {email_response.text}")

        print("\n" + "="*50)
        print(f"PHASE 4 COMPLETE FOR: {recipient_name}")
        print("="*50)
        
    except Exception as e:
        print(f"❌ Error during Phase 4 execution: {e}")

if __name__ == "__main__":
    main()
