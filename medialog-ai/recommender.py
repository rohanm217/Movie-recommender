import os
import json
import time
from dotenv import load_dotenv
from database import get_connection

load_dotenv()  # loads AI_PROVIDER / GEMINI_API_KEY from .env when running locally

# "ollama" runs a model on this machine (default — no API key, no rate limits).
# "gemini" calls Google's API, which is what makes cloud deployment possible.
PROVIDER = os.getenv("AI_PROVIDER", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
MAX_ATTEMPTS = 3
NUM_RECOMMENDATIONS = 6

# Ollama turns this into a grammar the model must follow. Without it, smaller
# models happily return a single object instead of an array.
RECOMMENDATION_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "media_type": {"type": "string", "enum": ["movie", "tv", "anime"]},
            "reason": {"type": "string"},
        },
        "required": ["title", "media_type", "reason"],
    },
    "minItems": NUM_RECOMMENDATIONS,
    "maxItems": NUM_RECOMMENDATIONS,
}

_client = None


class RecommendationError(Exception):
    """The request failed. Distinct from an empty list, which means the
    watch history is empty and there's nothing to recommend from."""


def _get_client():
    """Lazily create the Gemini client so importing this module doesn't
    require an API key to be set (e.g. when running on Ollama)."""
    global _client
    if _client is None:
        from google import genai

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RecommendationError(
                "GEMINI_API_KEY is not set. Add it to your .env file locally, "
                "or to your app's Secrets if deployed on Streamlit Cloud."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _generate_ollama(prompt):
    """Run the prompt against a model on this machine. Returns raw text."""
    import ollama

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            format=RECOMMENDATION_SCHEMA,
        )
        return response["message"]["content"]
    except Exception as e:
        message = str(e)
        if "not found" in message.lower():
            raise RecommendationError(
                f"The model '{OLLAMA_MODEL}' isn't downloaded yet. "
                f"Run: ollama pull {OLLAMA_MODEL}"
            ) from e
        raise RecommendationError(
            "Couldn't reach Ollama. Make sure it's running — open the Ollama "
            f"app, or run 'ollama serve' in a terminal. ({e})"
        ) from e


def _generate_gemini(prompt):
    """Call Gemini, retrying transient failures (server overload, rate limits)
    with a growing pause. Returns raw text."""
    from google.genai import errors

    delay = 2
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = _get_client().models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )
            return response.text
        except RecommendationError:
            raise  # missing API key — retrying won't help
        except Exception as e:
            code = getattr(e, "code", None)
            transient = isinstance(e, errors.ServerError) or code == 429

            if not transient:
                raise RecommendationError(f"Couldn't reach Gemini: {e}") from e

            if attempt == MAX_ATTEMPTS:
                if code == 429:
                    raise RecommendationError(
                        "Hit Gemini's free-tier rate limit. Wait a minute, then "
                        "hit Refresh."
                    ) from e
                raise RecommendationError(
                    "Gemini is busy right now — this is usually temporary. "
                    "Give it a moment and hit Refresh."
                ) from e

            time.sleep(delay)
            delay *= 2


def _generate(prompt):
    """Dispatch to whichever provider is configured."""
    if PROVIDER == "ollama":
        return _generate_ollama(prompt)
    if PROVIDER == "gemini":
        return _generate_gemini(prompt)
    raise RecommendationError(
        f"Unknown AI_PROVIDER '{PROVIDER}'. Use 'ollama' or 'gemini'."
    )


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
    """Send watch history to the configured AI provider and get back
    recommendations."""

    history = get_watch_history()

    if not history:
        return []

    prompt = f"""You are a movie/TV/anime recommendation expert.

Here is someone's watch history:
{history}

Based on their genres, ratings, and notes, recommend exactly {NUM_RECOMMENDATIONS}
new movies, shows, or anime they haven't listed above.

Respond with ONLY a JSON array of {NUM_RECOMMENDATIONS} objects, no other text,
no explanation, no markdown fences. Use exactly this structure:
[
  {{"title": "Example Title", "media_type": "movie", "reason": "1-2 sentence reason tied to their taste"}}
]
media_type must be exactly one of: movie, tv, anime"""

    raw = _generate(prompt)

    cleaned = _clean_json_response(raw)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RecommendationError(
            "The model returned something that wasn't valid JSON. Try again."
        ) from e

    # Smaller local models sometimes wrap the array in an object,
    # e.g. {"recommendations": [...]} — unwrap it rather than failing.
    if isinstance(parsed, dict):
        for value in parsed.values():
            if isinstance(value, list):
                return value
        raise RecommendationError(
            "The model returned JSON in an unexpected shape. Try again."
        )

    return parsed

if __name__ == "__main__":
    import pprint
    pprint.pprint(get_recommendations())
