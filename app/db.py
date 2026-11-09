"""SQLite logging. Synthetic conversations only. Set STORE_MESSAGES=false to omit text."""
import json
import sqlite3
import threading
from datetime import datetime, timezone
from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS turns (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT, turn INTEGER, user_message TEXT, reply TEXT,
  rule_level INTEGER, llm_level INTEGER, final_level INTEGER, route TEXT,
  escalated INTEGER, validation_ok INTEGER, violations TEXT, retries INTEGER,
  used_fallback INTEGER, classifier_failed INTEGER, risk_reasons TEXT, path TEXT,
  created_at TEXT
);
CREATE TABLE IF NOT EXISTS escalations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT, turn INTEGER, level INTEGER, reasons TEXT,
  simulated INTEGER, created_at TEXT
);
CREATE TABLE IF NOT EXISTS admin_notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT UNIQUE, turn INTEGER, level INTEGER, reasons TEXT,
  status TEXT, error TEXT, created_at TEXT, sent_at TEXT
);
"""


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path=None):
        self.conn = sqlite3.connect(path or config.DB_PATH, check_same_thread=False)
        self.conn.executescript(SCHEMA)
        self._lock = threading.Lock()

    def log_turn(self, s: dict):
        msg = s.get("user_message", "") if config.STORE_MESSAGES else ""
        rep = s.get("reply", "") if config.STORE_MESSAGES else ""
        with self._lock:
            self.conn.execute(
                "INSERT INTO turns (conversation_id, turn, user_message, reply, rule_level,"
                " llm_level, final_level, route, escalated, validation_ok, violations, retries,"
                " used_fallback, classifier_failed, risk_reasons, path, created_at)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    s.get("conversation_id"), s.get("turn"), msg, rep,
                    s.get("rule_level"), s.get("llm_level"), s.get("final_level"),
                    s.get("route"), int(s.get("escalated", False)),
                    int(s.get("validation_ok", False)),
                    json.dumps(s.get("violations", [])), s.get("retries", 0),
                    int(s.get("used_fallback", False)), int(s.get("classifier_failed", False)),
                    json.dumps(s.get("risk_reasons", [])), json.dumps(s.get("path", [])),
                    _now(),
                )
            )
            self.conn.commit()

    def log_escalation(self, conversation_id, turn, level, reasons):
        with self._lock:
            self.conn.execute(
                "INSERT INTO escalations (conversation_id, turn, level, reasons, simulated,"
                " created_at) VALUES (?,?,?,?,?,?)",
                (conversation_id, turn, level, json.dumps(reasons), 1, _now())
            )
            self.conn.commit()

    def claim_admin_notification(self, conversation_id, turn, level, reasons):
        """Reserve a notification for a conversation. If escalated to a higher level, allow re-notifying."""
        with self._lock:
            cur = self.conn.execute(
                "SELECT level, status FROM admin_notifications WHERE conversation_id=?",
                (conversation_id,)
            )
            row = cur.fetchone()
            if row is not None:
                existing_level, existing_status = row
                if level <= existing_level and existing_status in ("sent", "queued"):
                    return False
                # Update and allow re-notifying for higher level escalation
                self.conn.execute(
                    "UPDATE admin_notifications SET turn=?, level=?, reasons=?, status='queued', error='' WHERE conversation_id=?",
                    (turn, level, json.dumps(reasons), conversation_id)
                )
                self.conn.commit()
                return True
            try:
                self.conn.execute(
                    "INSERT INTO admin_notifications (conversation_id, turn, level, reasons, status, error, created_at) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (conversation_id, turn, level, json.dumps(reasons), "queued", "", _now()),
                )
                self.conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def update_admin_notification(self, conversation_id, status, error=""):
        with self._lock:
            sent_at = _now() if status == "sent" else None
            self.conn.execute(
                "UPDATE admin_notifications SET status=?, error=?, sent_at=? WHERE conversation_id=?",
                (status, error[:500], sent_at, conversation_id),
            )
            self.conn.commit()

