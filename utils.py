import os
import requests

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = "nikishabongale2021@gmail.com"  # Must be verified in SendGrid


def get_enriched_leads():
    leads = [{
        "name": "Alice Wright",
        "company": "BuildPro Ltd",
        "role": "CFO"
    }, {
        "name": "John Mason",
        "company": "AustraConstruct",
        "role": "Digital Transformation Lead"
    }, {
        "name": "Nina Evans",
        "company": "SteelMakers AU",
        "role": "CTO"
    }]
    for lead in leads:
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
        print("Response:", response.text")
    else:
        print(
            f"❌ Failed to send to {lead['email']} | Status: {response.status_code} | Msg: {response.text}"
        )

    return response.status_code
