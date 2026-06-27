from flask import Flask, request
import os
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
GMAIL_EMAIL = os.environ.get("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")


@app.route("/")
def home():
    return "WhatsApp Webhook is Running!"


@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Verification failed", 403


def send_email(subject, body):

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = GMAIL_EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


@app.route("/webhook", methods=["POST"])
def receive():

    data = request.json

    try:

        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return "OK", 200

        message = value["messages"][0]

        sender = message.get("from", "Unknown")

        msg_type = message.get("type", "unknown")

        text = ""

        if msg_type == "text":
            text = message["text"]["body"]
        else:
            text = f"<{msg_type} message>"

        contacts = value.get("contacts", [])

        name = sender

        if contacts:
            name = contacts[0]["profile"]["name"]

        body = f"""
New WhatsApp Message

Name:
{name}

Number:
{sender}

Type:
{msg_type}

Message:
{text}
"""

        send_email(
            f"WhatsApp Message from {name}",
            body
        )

    except Exception as e:
        print(e)

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)