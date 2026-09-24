import streamlit as sl
from database import get_connection
from add_entry import add_entry
from manage_entries import delete_entry, update_entry
from posters import get_poster_url
from recommender import get_recommendations

sl.set_page_config(page_title="WatchList AI", layout="centered")
sl.title("🎬 WatchList AI")

sl.header("Recommended For You")

if "recommendations" not in sl.session_state:
    sl.session_state.recommendations = None

col_a, col_b = sl.columns(2)
with col_a:
    if sl.button("Get Recommendations"):
        with sl.spinner("Thinking about what you'd like..."):
            sl.session_state.recommendations = get_recommendations()
with col_b:
    if sl.session_state.recommendations:
        if sl.button("🔄 Refresh"):
            with sl.spinner("Finding something new..."):
                sl.session_state.recommendations = get_recommendations()

if sl.session_state.recommendations == []:
    sl.write("Log a few titles first so I have something to base recommendations on!")
elif sl.session_state.recommendations:
    for rec in sl.session_state.recommendations:
        rec_title = rec.get("title", "Unknown")
        rec_type = rec.get("media_type", "movie")
        rec_reason = rec.get("reason", "")
        poster_url = get_poster_url(rec_title, rec_type)
        poster_html = f'<img src="{poster_url}" width="150">' if poster_url else ""

        sl.markdown(f"""
            <div style="text-align:center; margin-bottom: 25px;">
                {poster_html}
                <h4>{rec_title}</h4>
                <p style="color:gray; max-width:400px; margin:0 auto;">{rec_reason}</p>
            </div>
        """, unsafe_allow_html=True)

sl.divider()

sl.header("Your Watch List")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, title, media_type, genre, status, rating, notes FROM media ORDER BY id DESC")
rows = cursor.fetchall()
conn.close()

if not rows:
    sl.write("Nothing logged yet — add something below!")
else:
    for row in rows:
        entry_id, title, media_type, genre, status, rating, notes = row
        poster_url = get_poster_url(title, media_type)
        poster_html = f'<img src="{poster_url}" width="150">' if poster_url else ""

        with sl.container(border=True):
            sl.markdown(f"""
                <div style="text-align:center;">
                    {poster_html}
                    <h4>{title} ({media_type})</h4>
                    <p>Genre: {genre} | Status: {status} | Rating: {rating}/5</p>
                </div>
            """, unsafe_allow_html=True)
            if notes:
                sl.caption(notes)

            col1, col2 = sl.columns(2)
            with col1:
                with sl.expander("Edit"):
                    with sl.form(f"edit_form_{entry_id}"):
                        new_title = sl.text_input("Title", value=title)
                        new_type = sl.selectbox("Type", ["movie", "tv", "anime"],
                                                 index=["movie", "tv", "anime"].index(media_type))
                        new_genre = sl.text_input("Genre", value=genre)
                        new_status = sl.selectbox("Status",
                                                   ["completed", "in_progress", "want_to_watch", "dropped"],
                                                   index=["completed", "in_progress", "want_to_watch", "dropped"].index(status))
                        new_rating = sl.slider("Rating", 1, 5, rating if rating else 3)
                        new_notes = sl.text_area("Notes", value=notes if notes else "")
                        if sl.form_submit_button("Save Changes"):
                            update_entry(entry_id, new_title, new_type, new_genre, new_status, new_rating, new_notes)
                            sl.success("Updated!")
                            sl.rerun()
            with col2:
                if sl.button("Delete", key=f"delete_{entry_id}"):
                    delete_entry(entry_id)
                    sl.rerun()

sl.divider()

with sl.expander("➕ Add a new title"):
    with sl.form("add_form", clear_on_submit=True):
        title = sl.text_input("Title")
        media_type = sl.selectbox("Type", ["movie", "tv", "anime"])
        genre = sl.text_input("Genre")
        status = sl.selectbox("Status", ["completed", "in_progress", "want_to_watch", "dropped"])
        rating = sl.slider("Rating", 1, 5, 3)
        notes = sl.text_area("Notes (optional)")
        submitted = sl.form_submit_button("Add Entry")

        if submitted:
            if title.strip() == "":
                sl.error("Title can't be empty.")
            else:
                add_entry(title, media_type, genre, status, rating, notes)
                sl.success(f"Added '{title}'!")