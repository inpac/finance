import sqlite3
from config import DB_PATH

_conn: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(str(DB_PATH))
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
        _conn.execute("PRAGMA journal_mode = WAL")
    return _conn


def close_connection():
    global _conn
    if _conn:
        _conn.close()
        _conn = None
