# WRecs

A personal watch list for movies, TV, and anime, with recommendations generated
by AI based on what you've already logged.

Log what you've watched, rate it, leave notes — then hit **Get Recommendations**
and an AI model reads your history and suggests six things you haven't seen
yet, each with a reason tied to your actual taste. Posters for everything come
from TMDB.

Recommendations run on a **local model via Ollama** by default (no API key, no
rate limits, nothing leaves your machine), or on **Google's Gemini API** by
flipping one environment variable — which is what makes cloud deployment
possible.

## Features

- Log titles with type (movie/tv/anime), genre, status, 1–5 rating, and notes
- Edit or delete any entry inline from the dashboard
- Search the watch list by title/genre, and filter by type or status
- Poster art pulled automatically from TMDB
- Six AI recommendations laid out in a grid, with a Refresh button for a new set
- Watch list grid adapts to size: 2 across under 5 entries, 3 across after that
- Swap between a local model and Gemini with one environment variable

## Requirements

- Python 3.10+
- A [TMDB](https://www.themoviedb.org/settings/api) API key (free)
- For local recommendations: [Ollama](https://ollama.com) with a model pulled
- For Gemini recommendations: a [Gemini API key](https://aistudio.google.com/apikey)

## Setup

```bash
# 1. create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. pull the local model (skip if you're only using Gemini)
ollama pull llama3.1:8b

# 4. create the database
python database.py
```

Then create a `.env` file in the project root:

```
TMDB_API_KEY=your_tmdb_key_here

# "ollama" = local model (default), "gemini" = Google's API
AI_PROVIDER=ollama
GEMINI_API_KEY=your_gemini_key_here
```

## Choosing a provider

| | Ollama (local) | Gemini (cloud) |
| --- | --- | --- |
| Set | `AI_PROVIDER=ollama` | `AI_PROVIDER=gemini` |
| Cost | Free | Free tier, then paid |
| Needs | Ollama running locally | An API key |
| Speed | ~20s on an M-series Mac | ~3-5s |
| Deployable | No — local only | Yes |

Both models are overridable too: `OLLAMA_MODEL` (default `llama3.1:8b`) and
`GEMINI_MODEL` (default `gemini-3.6-flash`). Any Ollama model works — bigger
ones like `gemma3:12b` know more films but run slower.

## Running it

```bash
streamlit run app.py
```

The dashboard opens in your browser. Add a few titles first — recommendations
need a watch history to work from.

## Deploying to Streamlit Community Cloud

Ollama only runs on your own machine, so a deployed app has to use Gemini:

1. Push this repo to GitHub — **make sure `.env` is not committed** (see
   Security note below).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app
   pointing at `app.py`.
3. In the app's **Settings → Secrets**, add — note `AI_PROVIDER` must be
   `gemini` here, even though it's `ollama` locally:
   ```toml
   TMDB_API_KEY = "your_tmdb_key_here"
   AI_PROVIDER = "gemini"
   GEMINI_API_KEY = "your_gemini_key_here"
   ```
   Streamlit Community Cloud exposes these to the app as environment
   variables, so no code changes are needed between local and deployed runs.
4. `media_log.db` on the deployed app is separate from your local one and
   resets on redeploy — Streamlit Cloud's filesystem isn't persistent. For a
   watch list that needs to survive redeploys, swap SQLite for a hosted DB
   (e.g. Turso, Supabase, or a managed Postgres instance).

## Command line tools

The database can also be used without the dashboard:

```bash
python add_interactive.py   # add entries through terminal prompts
python view_entries.py      # print everything in the database
python recommender.py       # print recommendations as raw data
```

## Project layout

| File | What it does |
| --- | --- |
| `app.py` | The Streamlit dashboard — the main app |
| `database.py` | SQLite connection and table setup |
| `add_entry.py` | Inserts a new entry |
| `manage_entries.py` | Updates and deletes entries |
| `view_entries.py` | Prints all entries to the terminal |
| `add_interactive.py` | Terminal prompts for adding entries |
| `posters.py` | Looks up poster art from TMDB |
| `recommender.py` | Builds the prompt and calls Gemini for recommendations |
| `media_log.db` | The SQLite database file |

## Schema

The `media` table:

| Column | Type | Notes |
| --- | --- | --- |
| `id` | INTEGER | primary key |
| `title` | TEXT | required |
| `media_type` | TEXT | movie, tv, or anime |
| `genre` | TEXT | |
| `status` | TEXT | completed, in_progress, want_to_watch, dropped |
| `rating` | INTEGER | 1–5 |
| `notes` | TEXT | |
| `created_at` | TEXT | defaults to the current timestamp |

## Notes

- Both providers are constrained by a JSON schema (`RECOMMENDATION_SCHEMA` in
  `recommender.py`) so the model must return exactly 6 correctly-shaped
  results. Without it, smaller local models tend to return a single object
  instead of an array.
- On Gemini, transient failures (server overload, rate limits) are retried up
  to 3 times with a growing pause before giving up. Google also retires models
  over time — a 404 saying the model is unavailable means `GEMINI_MODEL` needs
  updating.
- If a request fails (Ollama not running, bad key, rate limit, network issue)
  or the response isn't valid JSON, the app shows the actual error rather than
  crashing. An empty result means only one thing: nothing is logged yet.
- Anime titles are searched against TMDB's TV endpoint, so anime films may not
  find a poster.

## Security note

`.env` currently contains real API keys and is tracked by git — if this repo
is ever made public (including for Streamlit Cloud deployment via GitHub),
those keys will be exposed. Before pushing publicly:

```bash
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
git rm --cached .env
git rm -r --cached __pycache__
```

Then rotate both API keys, since the old ones are already in git history.
