import os
import sys
import json
import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

from backend.processor import ReviewProcessor
from backend.gemini_client import GeminiClient

def send_email(analysis, recipient_email, recipient_name):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        print("❌ Error: SMTP credentials missing from environment.")
        return False

    try:
        subject = f"Weekly Pulse: INDMoney App Review Insights - {datetime.now().strftime('%B %d, %Y')}"
        
        # Build Email Body
        themes = "\n".join([f"{idx+1}. {t}" for idx, t in enumerate(analysis.get('themes', []))])
        quotes = "\n".join([f"{idx+1}. \"{q}\"" for idx, q in enumerate(analysis.get('quotes', []))])
        actions = "\n".join([f"{idx+1}. {a}" for idx, a in enumerate(analysis.get('actions', []))])
        
        body = f"""Hi {recipient_name},

Here is the weekly pulse for INDMoney based on the latest review analysis.

EXECUTIVE SUMMARY
{analysis.get('summary')}

TOP THEMES
{themes}

REAL USER QUOTES
{quotes}

ACTION IDEAS
{actions}

Best Regards,
INDMoney Product Insights Bot
"""

        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        
        print(f"🚀 SUCCESS: Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

def main():
    print(f"🏁 Starting Automated Pulse Generation: {datetime.now()}")
    
    # Configuration
    RECIPIENT_EMAIL = "Shraddha.jagtap14081996@gmail.com"
    RECIPIENT_NAME = "Shraddha"
    CSV_PATH = "data/sample_reviews.csv"
    WEEKS = 8
    MAX_REVIEWS = 200
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in environment.")
        sys.exit(1)

    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: {CSV_PATH} not found.")
        sys.exit(1)

    try:
        # 1. Process Reviews
        print(f"📊 Processing {CSV_PATH} (Last {WEEKS} weeks)...")
        processor = ReviewProcessor()
        reviews = processor.process_csv(CSV_PATH, weeks=WEEKS)
        reviews = reviews[:MAX_REVIEWS]
        
        if not reviews:
            print("⚠️ No reviews found for the specified period.")
            return

        # 2. Analyze with LLM
        print(f"🧠 Analyzing {len(reviews)} reviews with Gemini...")
        llm = GeminiClient(api_key=api_key)
        analysis = llm.analyze_reviews(reviews)
        
        # 3. Send Email
        print("📧 Dispatching weekly pulse email...")
        send_email(analysis, RECIPIENT_EMAIL, RECIPIENT_NAME)
        
        print(f"✅ Automated Pulse Generation Finished: {datetime.now()}")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
