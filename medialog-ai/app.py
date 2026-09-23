import streamlit as sl
from database import get_connection
from add_entry import add_entry
from manage_entries import delete_entry, update_entry
from posters import get_poster_url

sl.markdown("<h1 style='text-align: center;'>WRecs</h1>", unsafe_allow_html=True)
sl.markdown("<h2 style='text-align: center;'>Add a new title</h1>", unsafe_allow_html=True)


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

sl.header("Your Watch List")

conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT id, title, media_type, genre, status, rating, notes FROM media ORDER BY id DESC")
rows = cursor.fetchall()
conn.close()

if not rows:
    sl.write("Nothing logged yet — add something above!")
else:
    for row in rows:
        entry_id, title, media_type, genre, status, rating, notes = row
        with sl.container(border=True):
            sl.subheader(f"{title}  ({media_type})")
            poster_url = get_poster_url(title, media_type)
            if poster_url:
                sl.image(poster_url, width=150)
            sl.write(f"**Genre:** {genre} | **Status:** {status} | **Rating:** {rating}/5")
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
