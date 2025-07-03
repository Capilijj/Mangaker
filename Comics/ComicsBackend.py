# ComicsBackend.py

import sqlite3
from datetime import datetime, timedelta
from users_db import current_session
from user_model import add_bookmark, remove_bookmark_db, get_bookmarks_by_email, get_connection

# === DYNAMICALLY ADDED NEW MANGA LIST ===
# This list is for manga temporarily added during the session,
# not yet persisted to the database.
new_manga_list = [] # Make sure this is accessible globally or passed appropriately

# Helper function to sanitize string inputs (copied from adminBackend for consistency)
def _sanitize_string_input(value):
    if value is None:
        return ""
    s_value = str(value).strip()
    if s_value.lower() == "n/a" or s_value == "":
        return ""
    return s_value

# === Returns manga list directly from the database (Optimized with JOIN) ===
def get_manga_list(query=None, genre_filter=None, status_filter=None, order_filter=None, is_new_added_filter=False):
    # --- START MODIFICATION FOR "ADDED" FILTER ---
    # Ito ang pinaka-unang check para sa "Added" filter.
    # Kung ang filter ay "Added", ibabalik agad ang in-memory new_manga_list.
    if is_new_added_filter:
        sorted_new_manga = sorted(
            new_manga_list,
            key=lambda x: x.get("release_date", datetime.min), # Sort by release_date
            reverse=True # Newest first
        )
        return sorted_new_manga # AGAD IBALIK, HINDI NA DADAAN SA DATABASE QUERY
    # --- END MODIFICATION FOR "ADDED" FILTER ---

    mangas_from_db = []
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")

            sql_query = '''
                SELECT
                    M.mangaId,
                    M.title,
                    M.author,
                    M.latest,
                    M.status,
                    M.img_path,
                    M.description,
                    M.update_date,
                    GROUP_CONCAT(G.genre, ', ') AS genres_list
                FROM
                    Manga AS M
                LEFT JOIN
                    Genres AS G ON M.mangaId = G.mangaId
                WHERE 1=1 -- Dummy condition to allow easy addition of AND clauses
            '''
            params = []
            having_conditions = []
            having_params = []

            if query:
                sql_query += " AND LOWER(M.title) LIKE ?"
                params.append(f"%{_sanitize_string_input(query).lower()}%")

            # Handle status filter, potentially overridden by order filter
            effective_status_filter = status_filter # Simulan sa kasalukuyang status_filter

            # --- NEW LOGIC FOR "Unupdate" ORDER FILTER to force status ---
            if order_filter == "Unupdate":
                effective_status_filter = ["hiatus", "completed"] # I-force ang mga statuses na ito
            # --- END NEW LOGIC ---

            if effective_status_filter: # Gamitin ang effective_status_filter
                if isinstance(effective_status_filter, list):
                    placeholders = ', '.join(['?' for _ in effective_status_filter])
                    sql_query += f" AND LOWER(M.status) IN ({placeholders})"
                    params.extend([_sanitize_string_input(s).lower() for s in effective_status_filter])
                elif effective_status_filter != "All":
                    sql_query += " AND LOWER(M.status) = ?"
                    params.append(_sanitize_string_input(effective_status_filter).lower())

            sql_query += " GROUP BY M.mangaId, M.title, M.author, M.latest, M.status, M.img_path, M.description, M.update_date"

            if genre_filter and genre_filter != "All":
                having_conditions.append("LOWER(genres_list) LIKE ?")
                having_params.append(f"%{_sanitize_string_input(genre_filter).lower()}%")

            if having_conditions:
                sql_query += " HAVING " + " AND ".join(having_conditions)
                params.extend(having_params)

            # Apply order filter
            if order_filter == "A-Z":
                sql_query += " ORDER BY M.title ASC"
            elif order_filter == "Z-A":
                sql_query += " ORDER BY M.title DESC"
            elif order_filter == "Update":
                sql_query += " ORDER BY M.update_date DESC NULLS LAST"
            elif order_filter == "Popular":
                # For "Popular", we'll just sort by title for now.
                # If there's a 'views' or 'popularity_score' column, that would be used here.
                sql_query += " ORDER BY M.title ASC"
            elif order_filter == "Unupdate":
                # For "Unupdate", sort by update date ascending (oldest first)
                # Combined with the status filter above, this will show hiatus/completed, oldest update first.
                sql_query += " ORDER BY M.update_date ASC NULLS FIRST"
            else: # Default order if no specific order_filter is applied
                sql_query += " ORDER BY M.title ASC" # O kung ano man ang default mo

            # === DITO DAPAT I-EXECUTE ANG SQL QUERY, MINSAN LANG ===
            cursor.execute(sql_query, params)
            manga_rows = cursor.fetchall()

            for row in manga_rows:
                mangaId, title, author, latest, status, img_path, description, update_date, genres_str = row
                
                mangas_from_db.append({
                    "mangaId": mangaId,
                    "title": title,
                    "name": title,
                    "author": author,
                    "chapter": latest,
                    "genre": genres_str if genres_str else "",
                    "status": status,
                    "image": img_path,
                    "description": description,
                    "update_date": update_date
                })
    except sqlite3.Error as e:
        print(f"Database error in get_manga_list: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in get_manga_list: {e}")
    return mangas_from_db

# === Returns new manga list added via add_manga ===
def get_new_manga_list():
    return new_manga_list

# === Combine both database-sourced and new manga into one ===
def get_all_manga():
    """Returns all manga from both lists (DB and dynamically added)."""
    # Ensure no duplicates if manga are added to new_manga_list
    # and then also persisted to the database
    db_mangas = get_manga_list() # This will now return filtered/ordered if parameters are passed
    all_manga_dict = {m["mangaId"]: m for m in db_mangas if "mangaId" in m} # Use mangaId as unique key

    for new_manga in new_manga_list:
        # If new_manga has a title and not already in DB list, add it
        # Note: Dynamic new_manga_list items might not have mangaId yet
        if "title" in new_manga and new_manga["title"] not in [m.get("title") for m in db_mangas]:
             # Assign a temporary unique ID for new_manga_list items if needed for UI,
             # or simply append if UI handles missing mangaId
            all_manga_dict[f"new_{len(all_manga_dict)}"] = new_manga # Assign temporary key
            
    return list(all_manga_dict.values())


# === Adds a new manga into new_manga_list with release date ===
def add_manga(manga_details):
    # Check against both DB and dynamic list
    # Use is_new_added_filter=False to ensure get_manga_list queries the DB for existing titles
    all_current_titles = {m.get("title") for m in get_manga_list(is_new_added_filter=False)} 
    all_current_titles.update({m.get("name") for m in new_manga_list})

    if manga_details.get("name") in all_current_titles:
        return False, "Manga with this name already exists."

    manga_details.setdefault("release_date", datetime.now())
    new_manga_list.append(manga_details)
    return True, "New manga added successfully!"

# === Filters newly added manga based on recent release dates ===
def get_new_releases_backend(days_ago=30, limit=None):
    threshold_date = datetime.now() - timedelta(days=days_ago)
    new_releases = [
        m for m in new_manga_list
        if isinstance(m.get("release_date"), datetime) and m["release_date"] >= threshold_date
    ]
    new_releases.sort(key=lambda x: x.get("release_date", datetime.min), reverse=True)
    return new_releases[:limit] if limit else new_releases

# === Bookmarks a manga for the currently logged-in user ===
def bookmark_manga_admin(manga_to_bookmark):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    title = manga_to_bookmark.get("name") or manga_to_bookmark.get("title")
    if not title:
        return "Manga title missing."

    existing = get_bookmarks_by_email(email)
    if title in existing:
        return "Manga already bookmarked."

    success, msg = add_bookmark(email, title)
    return msg

# === Removes a bookmarked manga for the current user ===
def remove_bookmark_admin(manga_to_remove):
    email = current_session.get("email")
    if not email:
        return "No user logged in."

    title = manga_to_remove.get("name") or manga_to_remove.get("title")
    if not title:
        return "Manga title missing."

    removed = remove_bookmark_db(email, title)
    return "Bookmark removed successfully!" if removed else "Bookmark not found."