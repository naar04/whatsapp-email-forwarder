from flask import Flask, request
import os
import json
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
TO_EMAIL = os.getenv("TO_EMAIL", "")


def send_email(subject, body):

    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "from": "onboarding@resend.dev",
            "to": [TO_EMAIL],
            "subject": subject,
            "text": body
        },
        timeout=30
    )

    print("Resend status:", response.status_code)
    print("Resend response:", response.text)


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

        if "messages" not in value:
            print("Status update received")
            return "OK", 200

        message = value["messages"][0]

        sender = message.get("from", "Unknown")
        msg_type = message.get("type", "unknown")

        contacts = value.get("contacts", [])
        sender_name = sender

        if contacts:
            sender_name = contacts[0]["profile"]["name"]

        content = ""

        if msg_type == "text":
            content = message["text"]["body"]

        elif msg_type == "button":
            content = message["button"]["text"]

        elif msg_type == "image":
            content = "Image received"

        elif msg_type == "document":
            content = "Document received"

        elif msg_type == "audio":
            content = "Audio received"

        elif msg_type == "video":
            content = "Video received"

        else:
            content = f"{msg_type} message received"

        body = f"""
New WhatsApp Message

Name: {sender_name}

Number: {sender}

Type: {msg_type}

Content:
{content}
"""

        send_email(
            f"WhatsApp Message from {sender_name}",
            body
        )

        print("Email request sent to Resend")

    except Exception as e:

        print("ERROR:")
        print(str(e))

    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
