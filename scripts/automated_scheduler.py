import schedule
import time
import requests
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

load_dotenv()

# Setup Logging
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "scheduler.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

RECIPIENT_EMAIL = "Shraddha.jagtap14081996@gmail.com"
RECIPIENT_NAME = "Shraddha"
BACKEND_URL = "http://localhost:8000"

def run_weekly_pulse():
    logging.info("Starting automated pulse generation...")
    try:
        # 1. Run Pipeline (8 weeks, 200 reviews)
        payload = {
            "weeks": 8,
            "max_reviews": 200,
            "api_key": os.getenv("GEMINI_API_KEY")
        }
        logging.info("Triggering pipeline for last 8 weeks, max 200 reviews...")
        response = requests.post(f"{BACKEND_URL}/run-pipeline", json=payload)
        
        if response.status_code != 200:
            logging.error(f"Pipeline failed: {response.text}")
            return
            
        results = response.json()
        logging.info(f"Pipeline complete. Sending report to {RECIPIENT_EMAIL}...")
        
        # 2. Send Email
        email_payload = {
            "email": RECIPIENT_EMAIL,
            "name": RECIPIENT_NAME,
            "analysis": results
        }
        email_response = requests.post(f"{BACKEND_URL}/send-email", json=email_payload)
        
        if email_response.status_code == 200:
            logging.info(f"SUCCESS: Weekly Pulse sent successfully to {RECIPIENT_EMAIL}")
        else:
            logging.error(f"Email sending failed: {email_response.text}")
            
    except Exception as e:
        logging.exception(f"Error during scheduled task: {e}")

# Schedule the task every 5 minutes
schedule.every(5).minutes.do(run_weekly_pulse)

# For verification/immediate run uncomment below
# run_weekly_pulse()

logging.info("Automated Scheduler started.")
logging.info("Frequency: Every 5 minutes")
logging.info(f"Recipient: {RECIPIENT_EMAIL}")
logging.info("Constraints: 200 reviews, last 8 weeks")

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping scheduler...")
        break
    except Exception as e:
        logging.error(f"Scheduler loop error: {e}")
        time.sleep(60)
