import sqlite3
conn = sqlite3.connect("worldcup_2026.db")
conn.execute("DROP TABLE group_standings")
conn.commit()
conn.close()