import schedule
import time
import requests
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

RECIPIENT_EMAIL = "Shraddha.jagtap14081996@gmail.com"
RECIPIENT_NAME = "Shraddha"
BACKEND_URL = "http://localhost:8000"

def run_weekly_pulse():
    print(f"🕒 [{time.ctime()}] Starting scheduled weekly pulse...")
    try:
        # 1. Run Pipeline (8 weeks, 200 reviews)
        payload = {
            "weeks": 8,
            "max_reviews": 200,
            "api_key": os.getenv("GEMINI_API_KEY")
        }
        print(f"📡 Triggering pipeline for last 8 weeks, max 200 reviews...")
        response = requests.post(f"{BACKEND_URL}/run-pipeline", json=payload)
        
        if response.status_code != 200:
            print(f"❌ Pipeline failed: {response.text}")
            return
            
        results = response.json()
        print(f"✅ Pipeline complete. Sending report to {RECIPIENT_EMAIL}...")
        
        # 2. Send Email
        email_payload = {
            "email": RECIPIENT_EMAIL,
            "name": RECIPIENT_NAME,
            "analysis": results
        }
        email_response = requests.post(f"{BACKEND_URL}/send-email", json=email_payload)
        
        if email_response.status_code == 200:
            print(f"🚀 SUCCESS: Weekly Pulse sent successfully to {RECIPIENT_EMAIL}")
        else:
            print(f"❌ Email sending failed: {email_response.text}")
            
    except Exception as e:
        print(f"❌ Error during scheduled task: {e}")

# Schedule the task every Friday at 15:35 IST
schedule.every().friday.at("15:35").do(run_weekly_pulse)

# For verification/immediate run uncomment below
# run_weekly_pulse()

print(f"🚀 Automated Weekly Scheduler started.")
print(f"📅 Target: Every Friday at 3:35 PM IST")
print(f"📧 Recipient: {RECIPIENT_EMAIL}")
print(f"📊 Constraints: 200 reviews, last 8 weeks")

while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping scheduler...")
        break
    except Exception as e:
        print(f"⚠️ Scheduler loop error: {e}")
        time.sleep(60)
