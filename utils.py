import os
import requests
import csv
from datetime import datetime, timedelta

LOG_FILE = "outreach_log.csv"

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "nikishabongale2021@gmail.com"  # Must be verified in SendGrid


def get_enriched_leads():
    leads = [
        {
            "name": "Alice Wright",
            "company": "BuildPro Ltd",
            "role": "CFO"
        },
        {
            "name": "John Mason",
            "company": "AustraConstruct",
            "role": "Digital Transformation Lead"
        },
        {
            "name": "Nina Evans",
            "company": "SteelMakers AU",
            "role": "CTO"
        },
        {
            "name": "Nikisha Bongale",
            "company": "Reverend.ai",
            "role": "AI Agent Engineer",
            "email": "nikishabongale2021@gmail.com"  # 🔥 Your real test email
        }
    ]

    for lead in leads:
        if "email" not in lead:
            username = lead["name"].lower().replace(" ", ".")
            domain = lead["company"].lower().replace(" ", "") + ".com.au"
            lead["email"] = f"{username}@{domain}"

    return leads


def send_real_email(lead):
    if not SENDGRID_API_KEY:
        print("❌ Missing SENDGRID_API_KEY")
        return 401

    data = {
        "personalizations": [{
            "to": [{
                "email": lead["email"],
                "name": lead["name"]
            }],
            "subject":
            "Let's connect about AI for construction"
        }],
        "from": {
            "email": FROM_EMAIL,
            "name": "Nikisha from Reverend.ai"
        },
        "content": [{
            "type":
            "text/plain",
            "value":
            f"""Hi {lead['name']},

I’m reaching out to explore how Reverend.ai can help {lead['company']} with intelligent AI solutions in construction and manufacturing.

Would you be open to a short call next week?

Best regards,  
Nikisha Bongale  
AI Agent Engineer, Reverend.ai"""
        }]
    }

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(SENDGRID_API_URL, json=data, headers=headers)

    if response.status_code == 202:
        print(f"✅ Email sent to {lead['email']}")
        log_email_activity(lead, "sent")  # 👈 Add this line
    else:
        print(
            f"❌ Failed to send to {lead['email']} | Status: {response.status_code}"
        )
        log_email_activity(
            lead, f"failed:{response.status_code}")  # 👈 Log failures too

    return response.status_code


def log_email_activity(lead, status):
    log_entry = {
        "name": lead["name"],
        "email": lead["email"],
        "company": lead["company"],
        "role": lead["role"],
        "status": status,
        "timestamp": datetime.utcnow().isoformat()
    }

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=log_entry.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(log_entry)


def get_leads_due_for_followup():
    if not os.path.exists(LOG_FILE):
        return []

    leads_due = []
    seen_emails = set()

    with open(LOG_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        log = list(reader)

    for entry in log:
        email = entry["email"]
        status = entry["status"]
        timestamp = datetime.fromisoformat(entry["timestamp"])

        # Skip if already followed up or failed
        if status.startswith("failed") or status == "followed_up":
            continue

        # Skip if a newer log entry already updated this lead
        if email in seen_emails:
            continue

        # Check if it's been ≥3 days
        if datetime.utcnow() - timestamp >= timedelta(days=3):
            leads_due.append({
                "name": entry["name"],
                "email": entry["email"],
                "company": entry["company"],
                "role": entry["role"],
                "last_contacted": timestamp.isoformat()
            })
            seen_emails.add(email)

    return leads_due


def send_followup_email(lead):
    if not SENDGRID_API_KEY:
        print("❌ Missing SENDGRID_API_KEY")
        return 401

    data = {
        "personalizations": [{
            "to": [{
                "email": lead["email"],
                "name": lead["name"]
            }],
            "subject":
            "Just checking in — AI tools for construction"
        }],
        "from": {
            "email": FROM_EMAIL,
            "name": "Nikisha from Reverend.ai"
        },
        "content": [{
            "type":
            "text/plain",
            "value":
            f"""Hi {lead['name']},

Just following up on my earlier email — I wanted to see if {lead['company']} would be interested in exploring how our AI agents can help streamline construction and manufacturing operations.

Happy to schedule a quick 15-minute chat if that sounds good!

Warm regards,  
Nikisha Bongale  
AI Agent Engineer, Reverend.ai"""
        }]
    }

    headers = {
        "Authorization": f"Bearer {SENDGRID_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(SENDGRID_API_URL, json=data, headers=headers)

    if response.status_code == 202:
        print(f"📨 Follow-up sent to {lead['email']}")
        log_email_activity(lead, "followed_up")
    else:
        print(
            f"❌ Follow-up failed for {lead['email']} | {response.status_code}")
        log_email_activity(lead, f"followup_failed:{response.status_code}")

    return response.status_code
