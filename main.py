from fastapi import FastAPI, Request, Header, HTTPException
from utils import get_enriched_leads, send_real_email
from utils import get_leads_due_for_followup, send_followup_email
from typing import List
import hmac, hashlib
import os
from sendgrid.helpers.eventwebhook import EventWebhook, EventWebhookHeader
from pydantic import BaseModel
from typing import List
import os

app = FastAPI()
SENDGRID_PUBLIC_KEY = os.getenv("SENDGRID_WEBHOOK_PUBLIC_KEY")

SENDGRID_PUBLIC_KEY = os.getenv("SENDGRID_WEBHOOK_PUBLIC_KEY")

app = FastAPI()


@app.get("/")
def home():
  return {"message": "Lead Outreach Agent is running successfully!"}


# @app.post("/sendgrid-events")
# async def sendgrid_events(request: Request,
#                           x_signature: str = Header(...),
#                           x_timestamp: str = Header(...)):
#   # # Optional: Verify signature using HMAC SHA256
#   # if SENDGRID_SIGNING_KEY:
#   #   payload = await request.body()
#   #   signed = hmac.new(SENDGRID_SIGNING_KEY.encode(),
#   #                     x_timestamp.encode() + payload,
#   #                     hashlib.sha256).hexdigest()
#   #   if not hmac.compare_digest(signed, x_signature):
#   #     raise HTTPException(status_code=400, detail="Invalid signature")

#   events: List[dict] = await request.json()
#   processed = []
#   for event in events:
#     etype = event.get("event")
#     email = event.get("email")
#     if etype == "delivered":
#       processed.append({email: "delivered"})
#     elif etype == "bounce":
#       processed.append({email: "bounced"})
#     elif etype == "unsubscribed":
#       processed.append({email: "unsubscribed"})
#     # Extend logic as needed

#   return {"received": processed}


class Event(BaseModel):
  email: str
  event: str
  sg_event_id: str
  timestamp: float


@app.post("/sendgrid-events")
async def receive_events(request: Request, events: List[Event]):
  signature = request.headers.get(EventWebhookHeader.SIGNATURE)
  timestamp = request.headers.get(EventWebhookHeader.TIMESTAMP)
  # if signature and timestamp and SENDGRID_PUBLIC_KEY:
  #   validator = EventWebhook()
  #   body = await request.body()
  #   if not validator.verify_signature(SENDGRID_PUBLIC_KEY, body.decode(),
  #                                     signature, timestamp):
  #     raise HTTPException(status_code=400, detail="Invalid signature")
  for evt in events:
    if evt.event in ("delivered", "bounce"):
      print(f"Event '{evt.event}' for: {evt.email}")
  return {"received": True}


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


@app.get("/followup-due")
def get_followup_candidates():
  leads = get_leads_due_for_followup()
  return {"due_for_followup": leads}


@app.post("/send-followup")
def send_followups():
  leads = get_leads_due_for_followup()
  if not leads:
    return {"message": "No leads due for follow-up."}

  results = []
  for lead in leads:
    status = send_followup_email(lead)
    results.append({lead["email"]: status})

  return {"followup_status": results}
