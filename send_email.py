from mailjet_rest import Client
import os


def send_email(email_from, emails_to, subject, text, html):
    api_key = os.environ["MJ_APIKEY_PUBLIC"]
    api_secret = os.environ["MJ_APIKEY_PRIVATE"]
    mailjet = Client(auth=(api_key, api_secret))

    recipients = [{"Email": email} for email in emails_to]

    data = {
        "FromEmail": email_from,
        "FromName": "Stock Info",
        "Subject": subject,
        "Text-part": text,
        "Html-part": html,
        "Recipients": recipients,
    }
    mailjet.send.create(data=data)
