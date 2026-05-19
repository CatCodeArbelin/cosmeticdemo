import sqlite3
from datetime import datetime
from typing import Optional


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def init(self):
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    client_name TEXT,
                    client_message TEXT,
                    ai_variant_1 TEXT,
                    ai_variant_2 TEXT,
                    selected_reply TEXT,
                    status TEXT,
                    created_at TEXT
                )
                """
            )

    def create_message(self, source: str, client_name: str, client_message: str, status: str = "new") -> int:
        with self._conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO messages(source, client_name, client_message, status, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (source, client_name, client_message, status, datetime.utcnow().isoformat()),
            )
            return cur.lastrowid

    def update_ai_variants(self, message_id: int, v1: str, v2: str, status: str = "new"):
        with self._conn() as conn:
            conn.execute(
                "UPDATE messages SET ai_variant_1=?, ai_variant_2=?, status=? WHERE id=?",
                (v1, v2, status, message_id),
            )

    def set_status_and_reply(self, message_id: int, status: str, selected_reply: Optional[str] = None):
        with self._conn() as conn:
            conn.execute(
                "UPDATE messages SET status=?, selected_reply=? WHERE id=?",
                (status, selected_reply, message_id),
            )

    def get_message(self, message_id: int):
        with self._conn() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
            return dict(row) if row else None
