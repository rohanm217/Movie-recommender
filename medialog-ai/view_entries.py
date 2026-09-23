from database import get_connection

def view_entries():
    """Fetch and print every entry in the media table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM media")
    rows = cursor.fetchall()
    conn.close()
    conn.close()

    if not rows:
        print("No entries yet.")
        return
    for row in rows:
        id, title, media_type, genre, status, rating, notes, created_at = row
        print(f"[{id}] {title} ({media_type}) - {genre}")
        print(f"      Status: {status} | Rating: {rating}")
        if notes:
            print(f"     Notes: {notes}")
        print()

if __name__ == "__main__":
    view_entries()