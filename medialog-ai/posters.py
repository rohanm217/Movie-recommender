import os
import requests
from dotenv import load_dotenv

load_dotenv() #reads the .env file and loads into the environment

API_KEY = os.getenv("TMDB_API_KEY")

def get_poster_url(title, media_type):
    """Search TMDB for a title and return its poster image URL, or None if not found."""
    # defaults anime to tv
    search_type = "movie" if media_type == "movie" else "tv"

    url = f"https:/api.themoviedb.org/3/search/{search_type}"
    params = {
        "api_key": API_KEY,
        "query": title
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = data.get("results")
    if not results:
        return None
    
    poster_path = results[0].get("poster_path")
    if not poster_path:
        return None
    
    return f"https://image.tmdb.org/t/p/w342{poster_path}"

