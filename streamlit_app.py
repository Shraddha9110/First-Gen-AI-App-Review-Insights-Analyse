import streamlit as st
import pandas as pd
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.processor import ReviewProcessor
from backend.gemini_client import GeminiClient

# Page Config
st.set_page_config(page_title="INDmoney Weekly Pulse | Managed Backend", page_icon="📊", layout="wide")

# Load environment
load_dotenv()

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #0f172a;
    }
    .stApp {
        color: #94a3b8;
    }
    h1, h2, h3 {
        color: white !important;
    }
    .stButton>button {
        background-color: #6366f1;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #4f46e5;
        border: none;
        color: white;
    }
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

def send_email_logic(analysis, recipient_email, recipient_name):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    if not all([smtp_host, smtp_port, smtp_user, smtp_pass]):
        st.error("❌ SMTP credentials missing in environment/secrets.")
        return False

    try:
        subject = f"Weekly Pulse: INDMoney App Review Insights - {datetime.now().strftime('%B %d, %Y')}"
        
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
        return True
    except Exception as e:
        st.error(f"❌ Failed to send email: {e}")
        return False

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/4/4f/INDmoney_Logo.png", width=150)
    st.title("Admin Panel")
    st.info("Managed Backend for INDmoney Weekly Pulse")
    
    api_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    
    st.markdown("---")
    weeks = st.slider("Weeks of reviews", 4, 12, 8)
    max_reviews = st.number_input("Max reviews to fetch", 10, 1000, 200)

# Main UI
st.title("INDmoney Weekly Pulse")
st.write("Generate insights from Play Store reviews and automate reporting.")

tab1, tab2 = st.tabs(["📊 Analysis Dashboard", "📧 Email Distribution"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Run Analysis")
        uploaded_file = st.file_uploader("Upload Play Store CSV", type=['csv'])
        use_sample = st.checkbox("Or use data/sample_reviews.csv", value=True)
        
        if st.button("Generate Pulse Report"):
            target_path = "data/sample_reviews.csv" if use_sample else None
            
            if not target_path and not uploaded_file:
                st.warning("Please upload a file or select sample data.")
            else:
                with st.spinner("Analyzing reviews..."):
                    try:
                        processor = ReviewProcessor()
                        if uploaded_file:
                            # Save temp file
                            with open("temp_reviews.csv", "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            reviews = processor.process_csv("temp_reviews.csv", weeks=weeks)
                        else:
                            reviews = processor.process_csv(target_path, weeks=weeks)
                        
                        reviews = reviews[:max_reviews]
                        
                        llm = GeminiClient(api_key=api_key)
                        analysis = llm.analyze_reviews(reviews)
                        
                        st.session_state['last_analysis'] = analysis
                        st.success("Analysis Complete!")
                    except Exception as e:
                        st.error(f"Error: {e}")

    if 'last_analysis' in st.session_state:
        analysis = st.session_state['last_analysis']
        st.markdown("---")
        st.subheader("Insights Report")
        
        st.markdown(f"**Executive Summary:**\n\n_{analysis['summary']}_")
        
        cols = st.columns(3)
        with cols[0]:
            st.markdown("### Top Themes")
            for t in analysis['themes']:
                st.markdown(f"- {t}")
        with cols[1]:
            st.markdown("### User Quotes")
            for q in analysis['quotes']:
                st.markdown(f"> \"{q}\"")
        with cols[2]:
            st.markdown("### Action Ideas")
            for a in analysis['actions']:
                st.markdown(f"1. {a}")

with tab2:
    st.subheader("Send Weekly Pulse Email")
    if 'last_analysis' not in st.session_state:
        st.info("Please run an analysis first in the Analysis Dashboard.")
    else:
        email_col1, email_col2 = st.columns(2)
        with email_col1:
            rec_name = st.text_input("Recipient Name", "Shraddha")
            rec_email = st.text_input("Recipient Email", "Shraddha.jagtap14081996@gmail.com")
            
            if st.button("Send Email to Stakeholders"):
                with st.spinner("Sending email..."):
                    success = send_email_logic(st.session_state['last_analysis'], rec_email, rec_name)
                    if success:
                        st.balloons()
                        st.success(f"🚀 Weekly Pulse sent to {rec_email}")

# Footer
st.markdown("---")
st.caption("INDmoney Review Insights Analyzer • Managed Backend")
