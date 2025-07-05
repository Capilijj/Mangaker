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

def search_mangas(query=None):
    all_available_mangas = []

    # Add all manga from all sources
    for manga in get_mangas():
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")),
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")),
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })
    for manga in get_completed_manga():
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")),
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")),
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })
    for manga in get_latest_update():
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")),
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")),
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })
    for manga in get_manga_list():
        all_available_mangas.append({
            "title": _sanitize_string_input(manga.get("title") or manga.get("name")),
            "genre": _sanitize_string_input(manga.get("genre")),
            "summary": _sanitize_string_input(manga.get("summary") or manga.get("desc") or manga.get("description")),
            "status": _sanitize_string_input(manga.get("status")),
            "author": _sanitize_string_input(manga.get("author")),
            "image_path": manga.get("image_path") or manga.get("image"),
            "chapter": _sanitize_string_input(manga.get("chapter"))
        })

    # Remove duplicates by title
    unique_mangas = {}
    for manga in all_available_mangas:
        title_key = _sanitize_string_input(manga.get("title")).lower()
        if title_key and title_key not in unique_mangas:
            unique_mangas[title_key] = manga
    all_mangas_for_search = list(unique_mangas.values())

    # Only filter by title (case-insensitive, partial match)
    if query:
        query_lower = _sanitize_string_input(query).lower()
        filtered_results = [
            manga for manga in all_mangas_for_search
            if query_lower in _sanitize_string_input(manga.get("title", "")).lower()
        ]
        return filtered_results

    return all_mangas_for_search