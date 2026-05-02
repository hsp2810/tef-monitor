"""
TEF Calgary Registration Monitor
=================================
Polls https://www.afcalgary.ca/exams/tef/closed/ every 15 minutes.

When that URL stops going to the "closed" page and instead lands on
the "tef-registrations-open" page, it means new dates have been posted
and you get an email immediately.

Setup
-----
1. pip install requests
2. Fill in your Gmail address and App Password below
   (Gmail App Password: myaccount.google.com → Security → App passwords)
3. python tef_monitor.py
"""

import smtplib
import time
import logging
from email.mime.text import MIMEText
from datetime import datetime

import requests

# ── YOUR SETTINGS ─────────────────────────────────────────────────────────────
EMAIL_ADDRESS  = ""    # Gmail to send FROM
EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"     # 16-char Gmail App Password
NOTIFY_EMAIL   = "your_email@gmail.com"    # Where to receive the alert

CHECK_INTERVAL = 15 * 60                   # How often to check (seconds)
# ─────────────────────────────────────────────────────────────────────────────

CLOSED_URL = "https://www.afcalgary.ca/exams/tef/closed/"
OPEN_URL   = "tef-registrations-open"      # substring present in the open page URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M",
)


def is_open() -> tuple[bool, str]:
    """Returns (True, final_url) if registrations are open, else (False, final_url)."""
    resp = requests.get(
        CLOSED_URL,
        headers={"User-Agent": "Mozilla/5.0 (TEF-monitor)"},
        timeout=15,
        allow_redirects=True,
    )
    final = resp.url
    return (OPEN_URL in final, final)


def send_email(final_url: str) -> None:
    body = (
        f"TEF Canada registrations at AF Calgary are NOW OPEN!\n\n"
        f"Register here before seats sell out:\n"
        f"  {final_url}\n\n"
        f"Detected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Good luck!"
    )
    msg = MIMEText(body)
    msg["Subject"] = "TEF Calgary registrations are OPEN - act fast!"
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = NOTIFY_EMAIL

    with smtplib.SMTP("smtp.gmail.com", 587) as s:
        s.ehlo()
        s.starttls()
        s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        s.send_message(msg)

    logging.info("Email sent to %s", NOTIFY_EMAIL)


def main() -> None:
    logging.info("TEF monitor started. Checking every %d minutes.", CHECK_INTERVAL // 60)

    while True:
        try:
            open_, final_url = is_open()
            if open_:
                logging.info("OPEN! Redirected to: %s", final_url)
                send_email(final_url)
                logging.info("Notification sent. Stopping monitor.")
                break
            else:
                logging.info("Still closed. (%s)", final_url)
        except Exception as e:
            logging.error("Check failed: %s", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
