# SearchPage/searchBackend.py (Modified for case-insensitive exact match search)

from Homepage.homeBackend import get_mangas, get_popular_manga, get_latest_update
from Admin.adminBackend import get_manga_list

def search_mangas(query=None, genre_filter=None, status_filter=None, order_filter=None):
    # Consolidate all manga lists
    all_available_mangas = []
    
    # Add mangas from homeBackend (main list)
    all_available_mangas.extend(get_mangas())
    
    # Add popular mangas from homeBackend
    for manga in get_popular_manga():
        all_available_mangas.append({
            "title": manga.get("name"),
            "genre": manga.get("genre"),
            "summary": "N/A",
            "status": manga.get("status"),
            "author": "N/A",
            "image_path": manga.get("image"),
            "chapter": manga.get("chapter")
        })

    # Add latest update mangas from homeBackend
    for manga in get_latest_update():
        all_available_mangas.append({
            "title": manga.get("name"),
            "genre": manga.get("genre"),
            "summary": "N/A",
            "status": manga.get("status"),
            "author": "N/A",
            "image_path": manga.get("image"),
            "chapter": manga.get("chapter")
        })

    # Add mangas from adminBackend (comics backend)
    for manga in get_manga_list():
        all_available_mangas.append({
            "title": manga.get("name"),
            "genre": manga.get("genre"),
            "summary": "N/A",
            "status": manga.get("status"),
            "author": "N/A",
            "image_path": manga.get("image"),
            "chapter": manga.get("chapter")
        })

    # Remove duplicates based on 'title' if any
    unique_mangas = {}
    for manga in all_available_mangas:
        if manga.get("title") not in unique_mangas:
            unique_mangas[manga.get("title")] = manga
    all_mangas_for_search = list(unique_mangas.values())

    # Filter by query (title search)
    filtered_results = []
    if query:
        # --- MODIFICATION START ---
        # Changed to use .lower() for both query and title for case-insensitive exact match
        query_lower = query.lower()
        filtered_results = [
            manga for manga in all_mangas_for_search
            if query_lower == manga.get("title", "").lower()
        ]
        # --- MODIFICATION END ---
        if not filtered_results:
            return []
    else:
        filtered_results = list(all_mangas_for_search)

    # Apply genre filter
    if genre_filter and genre_filter != "All":
        filtered_results = [
            manga for manga in filtered_results
            if genre_filter.lower() in manga.get("genre", "").lower()
        ]

    # Apply status filter
    if status_filter and status_filter != "All":
        filtered_results = [
            manga for manga in filtered_results
            if manga.get("status", "").lower() == status_filter.lower()
        ]

    # Apply order filter
    if order_filter == "A-Z":
        filtered_results.sort(key=lambda x: x.get("title", "").lower())
    elif order_filter == "Z-A":
        filtered_results.sort(key=lambda x: x.get("title", "").lower(), reverse=True)

    return filtered_results