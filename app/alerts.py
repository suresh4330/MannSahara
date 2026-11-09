"""Privacy-preserving optional Gmail notification for crisis routes.

This is an admin notification for a student-project prototype. It is not an
emergency service and never sends the student's message or model reply.
"""
from __future__ import annotations

import smtplib
import ssl
import threading
from email.message import EmailMessage

from . import config


def enabled() -> bool:
    return bool(
        config.EMAIL_ALERTS_ENABLED
        and config.ADMIN_ALERT_EMAIL
        and config.GMAIL_SENDER_EMAIL
        and config.GMAIL_APP_PASSWORD
    )


def _send(store, conversation_id: str, turn: int, level: int, reasons: list[str]) -> None:
    print(f"\n[🚨 IMMEDIATE ADMIN ALERT] Sending alert to {config.ADMIN_ALERT_EMAIL} for conversation {conversation_id} (Level {level})")
    message = EmailMessage()
    message["Subject"] = f"🚨 MannSahara URGENT ALERT: Risk Level {level} Student Message Detected"
    message["From"] = config.GMAIL_SENDER_EMAIL
    message["To"] = config.ADMIN_ALERT_EMAIL
    message.set_content(
        f"🚨 IMMEDIATE ADMIN NOTIFICATION - MANNSAHARA SAFETY WORKFLOW\n\n"
        f"A student conversation has triggered an active safety risk alert!\n\n"
        f"Details:\n"
        f"• Conversation ID: {conversation_id}\n"
        f"• Turn: {turn}\n"
        f"• Risk Level: Level {level} ({'CRISIS' if level >= 3 else 'HIGH DISTRESS'})\n"
        f"• Safety Signals / Triggers: {', '.join(reasons) or 'risk rule triggered'}\n"
        f"• Action Taken: Crisis/Support protocol activated and emergency resources shared with the student.\n\n"
        f"Please check the administrative console at http://localhost:8000 or the Safety Overview at http://localhost:5173/safety immediately.\n"
    )
    sent = False
    last_err = ""
    # Attempt 1: Port 465 SSL
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=config.EMAIL_ALERT_TIMEOUT_SECONDS) as smtp:
            smtp.login(config.GMAIL_SENDER_EMAIL, config.GMAIL_APP_PASSWORD)
            smtp.send_message(message)
            sent = True
    except Exception as exc1:
        last_err = type(exc1).__name__
        # Attempt 2: Port 587 STARTTLS
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=config.EMAIL_ALERT_TIMEOUT_SECONDS) as smtp:
                smtp.ehlo()
                smtp.starttls(context=context)
                smtp.ehlo()
                smtp.login(config.GMAIL_SENDER_EMAIL, config.GMAIL_APP_PASSWORD)
                smtp.send_message(message)
                sent = True
        except Exception as exc2:
            last_err = f"{type(exc1).__name__}/{type(exc2).__name__}"

    if sent:
        print(f"[✅ ADMIN ALERT DELIVERED] Successfully emailed {config.ADMIN_ALERT_EMAIL}")
        store.update_admin_notification(conversation_id, "sent")
    else:
        print(f"[⚠️ ADMIN ALERT LOGGED] Email dispatch failed ({last_err}), but alert is securely recorded in database & dashboard.")
        store.update_admin_notification(conversation_id, "failed", last_err)


def notify_async(store, conversation_id: str, turn: int, level: int, reasons: list[str]) -> bool:
    """Queue one email and database alert immediately without delaying the student response."""
    claimed = store.claim_admin_notification(conversation_id, turn, level, reasons)
    if not claimed:
        return False
    if not enabled():
        print(f"\n[🚨 IMMEDIATE ADMIN ALERT LOGGED] Level {level} alert recorded for admin {config.ADMIN_ALERT_EMAIL or '(No email configured)'}. Gmail App Password needed for live email delivery.")
        return True
    threading.Thread(
        target=_send,
        args=(store, conversation_id, turn, level, reasons),
        daemon=True,
        name="mannsahara-admin-alert",
    ).start()
    return True


def send_test_alert(recipient: str | None = None) -> dict:
    target = recipient or config.ADMIN_ALERT_EMAIL
    sender = config.GMAIL_SENDER_EMAIL
    pwd = (config.GMAIL_APP_PASSWORD or "").strip()

    if not sender or not target:
        return {"success": False, "error": "Missing GMAIL_SENDER_EMAIL or ADMIN_ALERT_EMAIL in .env"}
    if not pwd or pwd == "12345678912345678":
        return {
            "success": False,
            "error": "GMAIL_APP_PASSWORD in .env is currently a dummy placeholder ('12345678912345678'). A real 16-character Google App Password from https://myaccount.google.com/apppasswords is required to authenticate with Google's mail servers."
        }

    msg = EmailMessage()
    msg["Subject"] = "🚨 MannSahara TEST ALERT: Verification Email"
    msg["From"] = sender
    msg["To"] = target
    msg.set_content(
        f"🚨 MannSahara Admin Alert Verification\n\n"
        f"This is a test notification confirming that live email alerts to {target} are active and working!\n\n"
        f"Whenever any student message triggers safety risk level 2 or 3, an alert will be immediately dispatched to this address."
    )

    errs = []
    # Attempt 1: Port 465 SSL
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=config.EMAIL_ALERT_TIMEOUT_SECONDS) as smtp:
            smtp.login(sender, pwd)
            smtp.send_message(msg)
            return {"success": True, "message": f"Successfully sent test email to {target} via port 465 SSL!"}
    except Exception as e1:
        errs.append(f"Port 465: {type(e1).__name__} ({e1})")

    # Attempt 2: Port 587 STARTTLS
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=config.EMAIL_ALERT_TIMEOUT_SECONDS) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(sender, pwd)
            smtp.send_message(msg)
            return {"success": True, "message": f"Successfully sent test email to {target} via port 587 STARTTLS!"}
    except Exception as e2:
        errs.append(f"Port 587: {type(e2).__name__} ({e2})")

    return {
        "success": False,
        "error": f"Failed to deliver email through Google SMTP. Details: {'; '.join(errs)}. Check that 2-Step Verification is active and the Google App Password is correct."
    }
