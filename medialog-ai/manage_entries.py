from database import get_connection

def delete_entry(entry_id):
    "remove an entry by its id"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM media WHERE id = ?" (entry_id,))
    conn.commit()
    conn.close()

def update_entry(entry_id, title, media_type, genre, status, rating, notes):
    """overwrite an existing entry's fields"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE media
        SET title = ?, , media_type = ?, genre = ?, status = ?, rating = ?, notes = ?
        WHERE id = ?
    """, (title, media_type, genre, status, rating, notes, entry_id))
    conn.commit()
    conn.close()