from dotenv import load_dotenv
import requests
import os
import smtplib
from email.message import EmailMessage

load_dotenv(override=True)

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
BREVO_API_KEY = os.getenv("BREVO_API_KEY")


def send_email(
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
):
    """Send email via Brevo HTTP API if BREVO_API_KEY is set (works on
    Render, which blocks SMTP ports on free tier), otherwise via SMTP
    (works locally)."""

    if BREVO_API_KEY:
        send_via_brevo(recipient, subject, text_body, html_body)
    else:
        send_via_smtp(recipient, subject, text_body, html_body)


def send_via_brevo(
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
):
    if not EMAIL_ADDRESS:
        raise ValueError("EMAIL_ADDRESS is not set (used as verified Brevo sender)")

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key": BREVO_API_KEY,
            "content-type": "application/json",
            "accept": "application/json",
        },
        json={
            "sender": {"email": EMAIL_ADDRESS, "name": "Deep Research"},
            "to": [{"email": recipient}],
            "subject": subject,
            "htmlContent": html_body,
            "textContent": text_body,
        },
        timeout=15,
    )

    if response.status_code >= 300:
        raise RuntimeError(
            f"Brevo API error {response.status_code}: {response.text}"
        )

    print(f"Email sent via Brevo to {recipient}")


def send_via_smtp(
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
):
    if not all([EMAIL_ADDRESS, EMAIL_SMTP_SERVER, EMAIL_APP_PASSWORD]):
        raise ValueError(
            "Missing email config: set EMAIL_ADDRESS, EMAIL_SMTP_SERVER, "
            "and EMAIL_APP_PASSWORD in your .env file (or set BREVO_API_KEY "
            "to send via the Brevo API instead)"
        )

    msg = EmailMessage()

    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient
    msg["Subject"] = subject

    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_SMTP_SERVER, 587, timeout=10) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)

    print(f"Email sent via SMTP to {recipient}")


pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


def push(message):
    print(f"Push: {message}")

    payload = {
        "user": pushover_user,
        "token": pushover_token,
        "message": message,
    }

    requests.post(pushover_url, data=payload)