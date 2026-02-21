import feedparser
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()  # loads variables from .env into environment
feed_url = "https://status.openai.com/feed.rss"
seen_ids = set()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECIPIENT_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

        print(f"[Email Sent] {subject}")
    except Exception as e:
        print(f"[Email Failed] {e}")

def extract_details(entry):
    soup = BeautifulSoup(entry.get("summary", ""), "html.parser")

    status = None
    for bold in soup.find_all("b"):
        text = bold.get_text(strip=True)
        if text.startswith("Status:"):
            status = text.replace("Status:", "").strip()
            break

    components = [li.get_text(strip=True) for li in soup.find_all("li")]
    return status, components

data = feedparser.parse(feed_url)
print("\n=== Historical Incidents ===\n")
for entry in reversed(data.entries):
    status, components = extract_details(entry)
    print("Title:", entry.title)
    print("Published:", entry.published)
    print("Status:", status)
    print("Affected Components:", components)
    print("-" * 50)
    seen_ids.add(entry.id)

print("\n=== Monitoring for New Incidents ===\n")
while True:
    time.sleep(100)  #860 requests/day
    try:
        data = feedparser.parse(feed_url)
        new_entries = []
        for entry in data.entries:
            if entry.id in seen_ids:
                break
            new_entries.append(entry)

        for entry in reversed(new_entries):
            status, components = extract_details(entry)

            print("NEW INCIDENT")
            print("Title:", entry.title)
            print("Published:", entry.published)
            print("Status:", status)
            print("Affected Components:", components)
            print("-" * 50)

            # Send email notification
            subject = f"[OpenAI Incident] {entry.title}"
            body = (
                f"Title: {entry.title}\n"
                f"Published: {entry.published}\n"
                f"Status: {status}\n"
                f"Affected Components: {', '.join(components) if components else 'N/A'}\n\n"
                f"Link: {entry.get('link', 'N/A')}"
            )
            send_email(subject, body)

            seen_ids.add(entry.id)

    except Exception as e:
        print(f"[Monitor Error] {e}")