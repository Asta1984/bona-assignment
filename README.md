# OpenAI Status Monitor

A lightweight Python script that automatically tracks and logs service incidents from the [OpenAI Status Page](https://status.openai.com) using its RSS feed — and sends you an email alert whenever a new incident is detected.

---

## Problem Statement

Manually refreshing a status page to check for outages doesn't scale. This script solves that by consuming the OpenAI Status RSS feed on a polling interval, detecting new incidents as they appear, and notifying you via email — all without a browser or UI.

The same approach can be extended to track 100+ status pages from different providers simultaneously by running multiple feed monitors concurrently (e.g., using threads or asyncio).

---

## Features

- Parses the OpenAI Status RSS feed (`https://status.openai.com/feed.rss`)
- Prints all historical incidents on startup (oldest first)
- Polls every 100 seconds for new incidents (~860 requests/day)
- Extracts affected components and current status from each incident
- Sends an email notification for every new incident detected
- Credentials managed securely via a `.env` file

---

## Project Structure

```
.
├── main.py          # Main script
├── .env                # Your credentials (never commit this)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone or download the project

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Install dependencies

```bash
uv pip install -r requirements.txt
```

### 3. Configure your `.env` file

Create a `.env` file in the same directory as `main.py`:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_sender@gmail.com
SENDER_PASSWORD=your_app_password
RECIPIENT_EMAIL=your_recipient@gmail.com
```

> **Important:** Gmail requires an **App Password**, not your regular account password.  
> Generate one at: Google Account → Security → 2-Step Verification → App Passwords.

### 4. Add `.env` to `.gitignore`

```gitignore
.env
```

---

## Running the Script

```bash
python main.py
```

### Sample Output

```
=== Historical Incidents ===

Title: API Latency Issues
Published: Mon, 10 Feb 2025 14:32:00 +0000
Status: Resolved
Affected Components: ['API', 'Chat Completions']
--------------------------------------------------

=== Monitoring for New Incidents ===

NEW INCIDENT
Title: Degraded Performance - Responses API
Published: Sat, 21 Feb 2026 09:15:00 +0000
Status: Investigating
Affected Components: ['Responses API']
--------------------------------------------------
[Email Sent] [OpenAI Incident] Degraded Performance - Responses API
```

---

## How It Works

1. On startup, the script fetches and prints all existing incidents from the RSS feed and stores their IDs in a `seen_ids` set.
2. Every 100 seconds, the feed is re-fetched.
3. Any entry whose ID is not in `seen_ids` is treated as a new incident.
4. New incidents are printed to the console and trigger an email notification.
5. The ID is then added to `seen_ids` to prevent duplicate alerts.

### Why RSS over page scraping?

RSS feeds are structured, lightweight, and designed for exactly this use case — polling for updates. Scraping the HTML status page would be brittle (layout changes break scrapers), heavier on bandwidth, and potentially against the provider's ToS. RSS scales cleanly to 100+ providers.

---

## Scaling to 100+ Status Pages

To monitor multiple providers simultaneously, wrap the polling logic in threads:

## Dependencies

| Package | Purpose |
|---|---|
| `feedparser` | Parse RSS/Atom feeds |
| `beautifulsoup4` | Extract status and components from HTML summaries |
| `python-dotenv` | Load credentials from `.env` file |

> `smtplib` and `email` are part of Python's standard library — no installation needed.

---

## Limitations

- `seen_ids` is in-memory only — restarting the script will re-print all historical incidents
- Does not detect *updates* to existing incidents (only new entries)
- Polling is time-based, not push-based (RSS does not support webhooks natively)