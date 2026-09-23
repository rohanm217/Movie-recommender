from add_entry import add_entry

def prompt_for_entry():
    """Ask the user questions in the terminal and collect their answers."""
    print("--- Add a new title ---")
    title = input("Title: ")
    media_type = input("Type (movie/tv/anime): ").lower()
    genre = input("Genre: ")
    status = input("Status (completed/in_progress/want_to_watch/dropped): ").lower()

    rating = input("Rating (1-5, leave blank if none): ")
    rating = int(rating) if rating.strip() else None

    notes = input("Notes (optional): ")
    notes = notes if notes.strip() else None

    return title, media_type, genre, status, rating, notes

def run():
    """Keep adding entries until the user is done."""
    while True:
        title, media_type, genre, status, rating, notes = prompt_for_entry()
        add_entry(title, media_type, genre, status, rating, notes)

        again = input("Add another? (y/n): ").lower()
        if again != "y":
            break

if __name__ == "__main__":
    run()


