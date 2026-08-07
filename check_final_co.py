import sqlite3
import pandas as pd

conn = sqlite3.connect("database/obe.db")

df = pd.read_sql_query(
    "SELECT * FROM final_co_attainment",
    conn
)

print(df)

conn.close()