import ollama
import json
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
            line += f" — notes: {notes}"
        lines.append(line)

    return "\n".join(lines)

def _clean_json_response(text):
    """Strip markdown code fences the model sometimes wraps JSON in."""
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()
    return text

def get_recommendations():
    """Send watch history to local AI model and get back recommendations."""

    history = get_watch_history()

    if not history:
        return []

    prompt = f"""You are a movie/TV/anime recommendation expert.

Here is someone's watch history:
{history}

Based on their genres, ratings, and notes, recommend exactly 6 new movies, shows, or anime
they haven't listed above.

Respond with ONLY a JSON array, no other text, no explanation, no markdown fences.
Use exactly this structure:
[
  {{"title": "Example Title", "media_type": "movie", "reason": "1-2 sentence reason tied to their taste"}}
]
media_type must be exactly one of: movie, tv, anime"""

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["message"]["content"]
    cleaned = _clean_json_response(raw)

    try:
        recommendations = json.loads(cleaned)
        return recommendations
    except json.JSONDecodeError:
        # Model didn't return valid JSON this time — fail gracefully
        return []

if __name__ == "__main__":
    import pprint
    pprint.pprint(get_recommendations())
