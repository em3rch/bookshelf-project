import requests

from flask import current_app


BASE_URL = "https://www.googleapis.com/books/v1/volumes" 
LANGUAGES = {
    "": "Any language",
    "ru": "Russian",
    "en": "English",
    "pl": "Polish",
    "de": "German",
    "fr": "French"
}


def search_books(query: str, lang: str = "") -> list[dict]:
    params = {
        "q": query,
        "fields": "items(id,volumeInfo(title,authors,publishedDate,pageCount,imageLinks,categories))",
        "printType": "books",
        "key": current_app.config["GOOGLE_BOOKS_API_KEY"],
        "maxResults": 40
    }

    if lang and lang in LANGUAGES:
        params["langRestrict"]=lang

    response = requests.get(
        BASE_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()
    items = data.get("items", [])

    books = []

    for item in items: # Will work, because for works on empty lists
        info = item.get("volumeInfo", {})

        books.append({
            "google_id": item.get("id", ""),
            "title": info.get("title", "Unknown title"),
            "authors": ", ".join(info.get("authors", [])) or "Unknown author",
            "year": _parse_year(info.get("publishedDate", "")),
            "description": info.get("description"),
            "pages": info.get("pageCount"),
            "genres": ", ".join(info.get("categories", [])),
            "cover_url": _secure_cover(
                info.get("imageLinks", {}).get("thumbnail") or
                info.get("imageLinks", {}).get("smallThumbnail")),
            })

    return books


def get_book(google_id: str) -> dict | None:
    response = requests.get(
        f"{BASE_URL}/{google_id}",
        params={"key": current_app.config["GOOGLE_BOOKS_API_KEY"]},
        timeout=10
    )

    if response.status_code == 404:
        return None

    response.raise_for_status() # Raise an error and stop consequent action of the program

    item = response.json()
    info = item.get("volumeInfo", {})

    return {
        "google_id": item.get("id", ""),
        "title": info.get("title", "Unknown title"),
        "authors": ", ".join(info.get("authors", [])) or "Unknown author",
        "year": _parse_year(info.get("publishedDate", "")),
        "genres": ", ".join(info.get("categories", [])),
        "description": info.get("description", ""),
        "pages": info.get("pageCount"),
        "publisher": info.get("publisher", ""),
        "language": info.get("language", ""),
        "cover_url": _secure_cover(
            info.get("imageLinks", {}).get("thumbnail") or
            info.get("imageLinks", {}).get("smallThumbnail"))

    }



def _parse_year(date_str: str | None) -> int | None:
    try:
        return int(date_str[:4]) if date_str else None
    except (ValueError, IndexError):
        return None


def _secure_cover(url: str | None) -> str | None:
    if not url:
        return None

    if url.startswith("http://"):
        return f"https://{url[7:]}"
    
    return url
