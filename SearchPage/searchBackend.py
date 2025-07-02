# SearchPage/searchBackend.py 

from Homepage.homeBackend import get_mangas, get_completed_manga, get_latest_update
from Comics.ComicsBackend import get_manga_list, new_manga_list

# Helper function to sanitize string inputs (copied from adminBackend for consistency)
def _sanitize_string_input(value):
    if value is None:
        return ""
    s_value = str(value).strip()
    if s_value.lower() == "n/a" or s_value == "":
        return ""
    return s_value

def search_mangas(query=None, genre_filter=None, status_filter=None, order_filter=None):
    # Consolidate all manga lists
    all_available_mangas = []
    
    # Add mangas from homeBackend (main list) - these should already be clean from homeBackend
    for manga in get_mangas():
        # Sanitize relevant fields for consistency
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")),
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")),
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })
    
    # Add completed mangas from homeBackend
    for manga in get_completed_manga():
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")), # Get actual summary/description
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")), # Get actual author
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })

    # Add latest update mangas from homeBackend
    for manga in get_latest_update():
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")), # Get actual summary/description
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")), # Get actual author
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })

    # Add mangas from adminBackend (comics backend)
    for manga in get_manga_list():
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")), # Get actual summary/description
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")), # Get actual author
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })

    # Remove duplicates based on 'title' if any
    unique_mangas = {}
    for manga in all_available_mangas:
        # Use sanitized title for deduplication
        title_key = _sanitize_string_input(manga.get("title")).lower()
        if title_key and title_key not in unique_mangas:
            unique_mangas[title_key] = manga
    all_mangas_for_search = list(unique_mangas.values())

    # --- ORDER BY LOGIC ---
    if order_filter == "Update":
        # Show only manga with status Ongoing
        filtered_results = [
            manga for manga in all_mangas_for_search
            if _sanitize_string_input(manga.get("status", "")).lower() == "ongoing"
        ]

    elif order_filter == "Unupdated":
        # Show manga with status Completed or Hiatus
        filtered_results = [
            manga for manga in all_mangas_for_search
            if _sanitize_string_input(manga.get("status", "")).lower() in ["completed", "hiatus"]
        ]

    elif order_filter == "Popular":
        # Show only popular manga that are Completed
        # Also ensure these are sanitized
        filtered_results = []
        for manga in get_completed_manga():
            if _sanitize_string_input(manga.get("status", "")).lower() == "completed":
                filtered_results.append({
                    "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
                    "genre": _sanitize_string_input(manga.get("genre")),
                    "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")),
                    "status": _sanitize_string_input(manga.get("status")),
                    "author": _sanitize_string_input(manga.get("author")),
                    "image_path": manga.get("image_path") or manga.get("image"),
                    "chapter": _sanitize_string_input(manga.get("chapter"))
                })
    
    elif order_filter == "Added":
        # Show mangas from new_manga_list
        # Ensure these are sanitized
        filtered_results = []
        for manga in new_manga_list:
            filtered_results.append({
                "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
                "genre": _sanitize_string_input(manga.get("genre")),
                "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")),
                "status": _sanitize_string_input(manga.get("status")),
                "author": _sanitize_string_input(manga.get("author")),
                "image_path": manga.get("image_path") or manga.get("image"),
                "chapter": _sanitize_string_input(manga.get("chapter"))
            })

    else:
        # Default: full list, apply filters below
        filtered_results = list(all_mangas_for_search)

    # Filter by query (title search)
    if query:
        query_lower = _sanitize_string_input(query).lower()
        filtered_results = [
            manga for manga in filtered_results
            if query_lower == _sanitize_string_input(manga.get("title", "")).lower()
        ]
        if not filtered_results:
            return []

    # Apply genre filter
    if genre_filter and genre_filter != "All":
        genre_filter_lower = _sanitize_string_input(genre_filter).lower()
        filtered_results = [
            manga for manga in filtered_results
            if genre_filter_lower in _sanitize_string_input(manga.get("genre", "")).lower()
        ]

    # Apply status filter
    if status_filter and status_filter != "All":
        status_filter_lower = _sanitize_string_input(status_filter).lower()
        filtered_results = [
            manga for manga in filtered_results
            if status_filter_lower == _sanitize_string_input(manga.get("status", "")).lower()
        ]

    # Apply order filter for A-Z and Z-A only
    if order_filter == "A-Z":
        filtered_results.sort(key=lambda x: _sanitize_string_input(x.get("title", "")).lower())
    elif order_filter == "Z-A":
        filtered_results.sort(key=lambda x: _sanitize_string_input(x.get("title", "")).lower(), reverse=True)

    if not filtered_results:
        return []

    return filtered_results