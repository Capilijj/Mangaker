# SearchPage/searchBackend.py 

from Homepage.homeBackend import get_mangas, get_popular_manga, get_latest_update
from Admin.adminBackend import get_manga_list, new_manga_list

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

    # --- ORDER BY LOGIC ---
    if order_filter == "Update":
        # Show only manga with status Ongoing
        filtered_results = [
            manga for manga in all_mangas_for_search
            if manga.get("status", "").lower() == "ongoing"
        ]

    elif order_filter == "Unupdated":
        # Show manga with status Completed or Hiatus
        filtered_results = [
            manga for manga in all_mangas_for_search
            if manga.get("status", "").lower() in ["completed", "hiatus"]
        ]

    elif order_filter == "Popular":
        # Show only popular manga that are Completed
        filtered_results = [
            {
                "title": manga.get("name"),
                "genre": manga.get("genre"),
                "summary": "N/A",
                "status": manga.get("status"),
                "author": "N/A",
                "image_path": manga.get("image"),
                "chapter": manga.get("chapter")
            }
            for manga in get_popular_manga()
            if manga.get("status", "").strip().lower() == "completed"
        ]
    
    elif order_filter == "Added":
        # Show mangas from new_manga_list
        filtered_results = [
            {
                "title": manga.get("name"),
                "genre": manga.get("genre"),
                "summary": "N/A",
                "status": manga.get("status"),
                "author": "N/A",
                "image_path": manga.get("image"),
                "chapter": manga.get("chapter")
            }
            for manga in new_manga_list
        ]


    else:
        # Default: full list, apply filters below
        filtered_results = list(all_mangas_for_search)

        # Filter by query (title search)
        if query:
            query_lower = query.lower()
            filtered_results = [
                manga for manga in filtered_results
                if query_lower == manga.get("title", "").lower()
            ]
            if not filtered_results:
                return []

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

    # Apply order filter for A-Z and Z-A only
    if order_filter == "A-Z":
        filtered_results.sort(key=lambda x: x.get("title", "").lower())
    elif order_filter == "Z-A":
        filtered_results.sort(key=lambda x: x.get("title", "").lower(), reverse=True)

    # ADD 
    if not filtered_results:
        return []

    return filtered_results