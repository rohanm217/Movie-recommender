import streamlit as sl
from database import get_connection
from add_entry import add_entry

sl.title("WRecs")

sl.header("Add a new title")

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
            sl.error("File can't be empty")
        else:
            add_entry(title, media_type, genre, status, rating, notes)
            sl.success(f"Added '{title}'!")

sl.header("Your Watch list")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT title, media_type, genre, status, rating, notes FROM media ORDER BY id DESC")
rows = cursor.fetchall()
conn.close()

if not rows:
    sl.write("Nothing logged yet. Log something in to get recommendations")
else:
    for row in rows:
        title, media_type, genre, status, rating, notes = row
        with sl.container(border=True):
            sl.subheader(f"{title} ({media_type})")
            sl.write(f"Genre {genre} | Status {status} | Rating {rating}/5")
            if notes:
                sl.caption(notes)
