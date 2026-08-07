import sqlite3
import pandas as pd

conn = sqlite3.connect("database/obe.db")

df = pd.read_sql_query(
    """
    SELECT *
    FROM co_po_mapping
    ORDER BY po_no, co_no
    """,
    conn
)

print(df)

conn.close()