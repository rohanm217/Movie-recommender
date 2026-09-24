# WRecs

A personal watch list for movies, TV, and anime, with recommendations generated
by a local AI model based on what you've already logged.

Log what you've watched, rate it, leave notes — then hit **Get Recommendations**
and a local Llama model reads your history and suggests six things you haven't
seen yet, each with a reason tied to your actual taste. Posters for everything
come from TMDB.

## Features

- Log titles with type (movie/tv/anime), genre, status, 1–5 rating, and notes
- Edit or delete any entry inline from the dashboard
- Poster art pulled automatically from TMDB
- Six AI recommendations laid out in a grid, with a Refresh button for a new set
- Watch list grid adapts to size: 2 across under 5 entries, 3 across after that
- Everything stored locally in SQLite — nothing leaves your machine except
  poster lookups

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally with the `llama3.2` model
- A [TMDB](https://www.themoviedb.org/settings/api) API key (free)

## Setup

```bash
# 1. create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. install dependencies
pip install streamlit requests python-dotenv ollama

# 3. pull the AI model
ollama pull llama3.2

# 4. create the database
python database.py
```

Then add your TMDB key to a `.env` file in the project root:

```
TMDB_API_KEY=your_key_here
```

## Running it

Make sure Ollama is running, then:

```bash
streamlit run app.py
```

The dashboard opens in your browser. Add a few titles first — recommendations
need a watch history to work from.

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
| `recommender.py` | Builds the prompt and calls Ollama for recommendations |
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

- If the model returns something that isn't valid JSON, the recommendation call
  returns an empty list rather than crashing — just hit Refresh.
- Anime titles are searched against TMDB's TV endpoint, so anime films may not
  find a poster.
