"""
Database Connection
OBE Analytics Pro v1.0.0
"""

import sqlite3
from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database File
DB_PATH = BASE_DIR / "database" / "obe.db"


def get_connection():
    """
    Returns SQLite connection.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn