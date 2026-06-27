# WhatsApp Email Forwarder

This project receives incoming WhatsApp Cloud API messages through a webhook and forwards them to an email address using Gmail SMTP.

## Features

- Webhook verification
- Receives incoming WhatsApp messages
- Sends email notifications
- Supports text and non-text message notifications
- Ready for deployment on Render

## Environment Variables

- VERIFY_TOKEN
- GMAIL_EMAIL
- GMAIL_APP_PASSWORD
- TO_EMAIL