import sqlite3

DB_name = "media_log.db"

def get_connection():
    """Opens connection to the SQL Database file"""
    return sqlite3.connect(DB_name)

def init_db():
    """Creates the table if it doesn't already exist"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS media (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            title TEXT NOT NULL,
            media_type TEXT NOT NULL,
            genre TEXT,
            status TEXT NOT NULL, 
            rating INTEGER,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("Database ready.")

if __name__ == "__main__":
    init_db()