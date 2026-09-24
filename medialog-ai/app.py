import streamlit as sl
from database import get_connection
from add_entry import add_entry
from manage_entries import delete_entry, update_entry
from posters import get_poster_url
from recommender import get_recommendations

sl.set_page_config(page_title="WatchList AI", layout="wide")
sl.markdown("<h1 style='text-align:center;'>WRecs</h1>", unsafe_allow_html=True)

sl.markdown("<h2 style='text-align:center;'>Recommended For You</h2>", unsafe_allow_html=True)

if "recommendations" not in sl.session_state:
    sl.session_state.recommendations = None

# On its own, Get Recommendations is dead center; once there are results,
# it shifts left to make room for Refresh sitting right beside it.
if sl.session_state.recommendations:
    _, col_get, col_refresh, _ = sl.columns([2, 1.4, 1.4, 2])
else:
    _, col_get, _ = sl.columns([2, 1.4, 2])
    col_refresh = None

with col_get:
    if sl.button("Get Recommendations", use_container_width=True):
        with sl.spinner("Thinking about what you'd like..."):
            sl.session_state.recommendations = get_recommendations()
        sl.rerun()  # redraw so Refresh appears next to the button right away

if col_refresh is not None:
    with col_refresh:
        if sl.button("Refresh", use_container_width=True):
            with sl.spinner("Finding something new..."):
                sl.session_state.recommendations = get_recommendations()
            sl.rerun()

if sl.session_state.recommendations == []:
    sl.markdown(
        "<p style='text-align:center;'>Log a few titles first so I have something to base recommendations on!</p>",
        unsafe_allow_html=True,
    )
elif sl.session_state.recommendations:
    recs = sl.session_state.recommendations[:6]
    for start in range(0, len(recs), 3):
        cols = sl.columns(3)
        for col, rec in zip(cols, recs[start:start + 3]):
            rec_title = rec.get("title", "Unknown")
            rec_type = rec.get("media_type", "movie")
            rec_reason = rec.get("reason", "")
            poster_url = get_poster_url(rec_title, rec_type)
            poster_html = (
                f'<img src="{poster_url}" style="height:200px; border-radius:6px;">'
                if poster_url else ""
            )

            # Kept on one line: indented HTML gets read as a markdown code block.
            with col:
                sl.markdown(
                    f'<div style="text-align:center; margin-bottom:25px;">{poster_html}'
                    f'<h4 style="margin:8px 0 4px 0;">{rec_title}</h4>'
                    f'<p style="color:gray; font-size:0.85rem;">{rec_reason}</p></div>',
                    unsafe_allow_html=True,
                )

sl.divider()

sl.markdown("<h2 style='text-align:center;'>Your Watch List</h2>", unsafe_allow_html=True)

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, title, media_type, genre, status, rating, notes FROM media ORDER BY id DESC")
rows = cursor.fetchall()
conn.close()

if not rows:
    sl.markdown(
        "<p style='text-align:center;'>Nothing logged yet — add something below!</p>",
        unsafe_allow_html=True,
    )
else:
    # Small lists sit fine in a 2-wide grid; once there are 5+ entries, go 3-wide.
    per_row = 2 if len(rows) < 5 else 3
    for start in range(0, len(rows), per_row):
        cols = sl.columns(per_row)
        for col, row in zip(cols, rows[start:start + per_row]):
            entry_id, title, media_type, genre, status, rating, notes = row
            poster_url = get_poster_url(title, media_type)
            poster_html = (
                f'<img src="{poster_url}" style="height:170px; border-radius:6px;">'
                if poster_url else ""
            )

            with col, sl.container(border=True):
                sl.markdown(
                    f'<div style="text-align:center;">{poster_html}'
                    f'<h4 style="margin:8px 0 4px 0;">{title} ({media_type})</h4>'
                    f'<p style="font-size:0.85rem;">Genre: {genre} | Status: {status} | '
                    f'Rating: {rating}/5</p></div>',
                    unsafe_allow_html=True,
                )
                if notes:
                    sl.caption(notes)

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
                if sl.button("Delete", key=f"delete_{entry_id}", use_container_width=True):
                    delete_entry(entry_id)
                    sl.rerun()

sl.divider()

form_left, form_center, form_right = sl.columns([1, 2, 1])
with form_center, sl.expander("➕ Add a new title"):
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