from fastapi import FastAPI
from utils import get_enriched_leads, send_real_email

app = FastAPI()


@app.get("/")
def home():
  return {"message": "Lead Outreach Agent is running successfully!"}


@app.get("/leads")
def list_leads():
  leads = get_enriched_leads()
  return {"leads": leads}


@app.post("/send-emails")
def send_emails():
  leads = get_enriched_leads()
  statuses = []
  for lead in leads:
    status = send_real_email(lead)
    statuses.append({lead["email"]: status})
  return {"status": statuses}
