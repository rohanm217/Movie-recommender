import ollama
from database import get_connection

def get_watch_history():
    """pulls everything you've logged into db, formats as plain text for the AI"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title, media_type, genre, status, rating, notes FROM media")
    rows = cursor.fetchall()
    conn.close()

    lines = []
    for title, media_type, genre, status, rating, notes in rows:
        line = f"- {title} ({media_type}, genre: {genre}, status: {status}"
        if rating:
            line += f", rating: {rating}/5"
        line += ")"
        if notes:
            line += f" - notes: {notes}"
        lines.append(line)
    
    return "\n".join(lines)

def get_recommendations():
    """Send watch history to local AI model and get back recommendations."""
    history = get_watch_history()

    if not history:
        return "Log a few titles you have watched so I can give you some recommendations!"
    
    prompt = f"""You are a movie/TV/anime recommendation expert.

Here is someone's watch history:
{history}

Based on their genres, ratings, and notes, recommend 5 new movies, shows, or anime
they haven't listed above. For each recommendation, give the title and a 1-2 sentence
reason tied specifically to their taste patterns. Format as a numbered list."""
    
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]

if __name__ == "__main__":
    print(get_recommendations())