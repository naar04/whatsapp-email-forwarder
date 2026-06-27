from flask import Flask, request
import os
import json
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
TO_EMAIL = os.getenv("TO_EMAIL", "")


def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


@app.route("/")
def home():
    return "WhatsApp Email Forwarder is running!"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def receive():

    data = request.get_json(silent=True)

    print("========== WEBHOOK RECEIVED ==========")
    print(json.dumps(data, indent=2))

    try:

        value = data["entry"][0]["changes"][0]["value"]

        # Ignore status updates
        if "messages" not in value:
            print("No messages found. Probably a status update.")
            return "OK", 200

        message = value["messages"][0]

        sender = message.get("from", "Unknown")
        msg_type = message.get("type", "unknown")

        contacts = value.get("contacts", [])
        sender_name = sender

        if contacts:
            sender_name = contacts[0]["profile"]["name"]

        if msg_type == "text":
            content = message["text"]["body"]

        elif msg_type == "image":
            content = "📷 Image received"

        elif msg_type == "document":
            content = "📄 Document received"

        elif msg_type == "audio":
            content = "🎤 Audio received"

        elif msg_type == "video":
            content = "🎥 Video received"

        elif msg_type == "location":
            content = "📍 Location received"

        else:
            content = f"{msg_type} message received"

        body = f"""
New WhatsApp Message

Name:
{sender_name}

Number:
{sender}

Message Type:
{msg_type}

Content:
{content}
"""

        print("Sending email...")

        send_email(
            f"WhatsApp: {sender_name}",
            body
        )

        print("Email sent successfully.")

    except Exception as e:

        print("ERROR:")
        print(str(e))

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
