"""
Standalone test script for fetching book cover from OpenLibrary API
and generating an Amazon India search link.
Run with: python test.py
"""

import requests
import urllib.parse

def fetch_cover_via_openlibrary(title, author):
    """
    Search OpenLibrary for title+author, grab the first cover_i or ISBN,
    and return the medium‐size cover URL.
    """
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": title, "author": author, "limit": 1},
            timeout=5
        )
        data = resp.json()
        docs = data.get("docs", [])
        if not docs:
            return None

        doc = docs[0]
        # 1) Try cover_i
        if doc.get("cover_i"):
            cover_id = doc["cover_i"]
            return f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
        # 2) Fallback to ISBN
        if doc.get("isbn"):
            isbn = doc["isbn"][0]
            return f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
    except Exception as e:
        print(f"[fetch_cover] error: {e}")
    return None

def generate_amazon_in_link(book_title, author):
    query = f"{book_title} {author} book"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.amazon.in/s?k={encoded_query}"

def main():
    title = "The Silent Patient"
    author = "Alex Michaelides"

    print("Testing fetch_cover_via_openlibrary...")
    cover_url = fetch_cover_via_openlibrary(title, author)
    print(f"Cover URL: {cover_url}")
    assert cover_url is None or cover_url.startswith("https://covers.openlibrary.org/"), \
        "Invalid cover URL"

    print("Testing generate_amazon_in_link...")
    amzn_link = generate_amazon_in_link(title, author)
    print(f"Amazon Link: {amzn_link}")
    assert "amazon.in/s?k=" in amzn_link, "Invalid Amazon India link"

    print("All tests passed!")

if __name__ == "__main__":
    main()
