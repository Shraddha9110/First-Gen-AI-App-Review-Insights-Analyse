# INDMoney Review Insights Analyzer (Groq LLM)

Turn recent INDMoney Play Store reviews into a one-page weekly pulse containing top themes, user quotes, and action ideas.

## Features
- **Intelligent Theme Extraction**: Uses Groq LLM to group INDMoney reviews into 3-5 key themes.
- **Privacy First**: Automatically strips PII before analysis.
- **Actionable Insights**: Generates 3 specific action ideas for the INDMoney product team.

## How This Helps Teams
| Team | Impact |
| :--- | :--- |
| **Product/Growth** | Understand what features to fix or build next for INDMoney. |
| **Support** | Know what users are saying & acknowledge recurring issues. |
| **Leadership** | Quick weekly health pulse of the INDMoney app ecosystem. |

## Setup & Running

### 1. Backend (FastAPI)
- Install dependencies: `pip install fastapi uvicorn groq pandas pandas pydantic-settings fpdf2 python-multipart`
- Run the server: `uvicorn backend.main:app --reload`
- The backend will run on `http://localhost:8000`

### 2. Frontend
- Open `frontend/index.html` in your browser.
- Enter your **Groq API Key** in the provide field.
- Upload a CSV/JSON review export.

### 3. How to re-run for a new week
Simply export your latest 8-12 weeks of reviews from App Store Connect or Google Play Console and upload the new file to the dashboard.

## Theme Legend
The LLM dynamically generates themes based on your data. Common themes include:
- **Performance**: Speed, loading times, crashes.
- **UX/UI**: Ease of use, navigation, aesthetics.
- **Feature Requests**: User suggestions for new functionality.
- **Reliability**: Bug reports and stability.

## Project Structure
- `backend/`: FastAPI logic, LLM client, and review processing.
- `frontend/`: Vanilla HTML/CSS/JS dashboard.
- `data/`: Temporary storage and sample data.
- `data/reports/`: Generated PDF reports.
