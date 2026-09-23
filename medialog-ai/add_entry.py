from database import get_connection

def add_entry(title, media_type, genre, status, rating=None, notes=None):
    """Insert a new watced/watching/planned title into the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO media (title, media_type, genre, status, rating, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, media_type, genre, status, rating, notes))
    conn.commit()
    conn.close()
    print(f"Added: {title} ({media_type})")

