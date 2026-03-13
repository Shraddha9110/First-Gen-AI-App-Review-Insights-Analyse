from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .processor import ReviewProcessor
from .gemini_client import GeminiClient
from .report_generator import ReportGenerator
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import shutil

# Load environment variables from .env
load_dotenv()

app = FastAPI(title="Review Insights Analyzer")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = ReviewProcessor()
report_gen = ReportGenerator()

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...), api_key: str = None):
    if not file.filename.endswith(('.csv', '.json')):
        raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported")

    temp_path = f"data/{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if file.filename.endswith('.csv'):
            reviews = processor.process_csv(temp_path)
        else:
            reviews = processor.process_json(temp_path)

        llm = GeminiClient(api_key=api_key)
        results = llm.analyze_reviews(reviews)
        
        # Save results for export
        results['id'] = file.filename
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/run-pipeline")
async def run_pipeline(data: dict):
    # This endpoint processes the local sample_reviews.csv
    file_path = "data/sample_reviews.csv"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="sample_reviews.csv not found in data/ directory")
    
    weeks = data.get("weeks", 8)
    max_reviews = data.get("max_reviews", 1000)
    api_key = data.get("api_key")

    try:
        reviews = processor.process_csv(file_path, weeks=weeks)
        # Apply max_reviews limit
        reviews = reviews[:max_reviews]
        
        llm = GeminiClient(api_key=api_key)
        results = llm.analyze_reviews(reviews)
        results['id'] = "local_pipeline_run"
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export")
async def export_report(data: dict):
    try:
        file_path = report_gen.generate_pdf(data)
        return FileResponse(file_path, media_type='application/pdf', filename="weekly_pulse.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/send-email")
async def send_email(data: dict):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    recipient_email = data.get("email")
    recipient_name = data.get("name", "Team")
    analysis = data.get("analysis")

    if not recipient_email or not analysis:
        raise HTTPException(status_code=400, detail="Missing required email data")

    # SMTP Config from Env
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        raise HTTPException(status_code=500, detail="SMTP server is not configured in .env")

    try:
        subject = f"Weekly Pulse: INDMoney App Review Insights - Week of March 12, 2026"
        
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

        return {"status": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
