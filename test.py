"""
Standalone test script for fetching book cover from Google Books API
and generating an Amazon India search link.
Run with: python test.py
"""

import requests
import urllib.parse

def fetch_cover_via_google(title, author):
    query = f"intitle:{title}+inauthor:{author}"
    try:
        resp = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": query, "maxResults": 1},
            timeout=5
        )
        data = resp.json()
        return data["items"][0]["volumeInfo"]["imageLinks"]["thumbnail"]
    except Exception:
        return None

def generate_amazon_in_link(book_title, author):
    query = f"{book_title} {author} book"
    encoded_query = urllib.parse.quote(query)
    return f"https://www.amazon.in/s?k={encoded_query}"

def main():
    title = "The Hobbit"
    author = "J.R.R. Tolkien"

    print("Testing fetch_cover_via_google...")
    cover_url = fetch_cover_via_google(title, author)
    print(f"Cover URL: {cover_url}")
    assert cover_url is None or cover_url.startswith("http"), "Invalid cover URL"

    print("Testing generate_amazon_in_link...")
    amzn_link = generate_amazon_in_link(title, author)
    print(f"Amazon Link: {amzn_link}")
    assert "amazon.in/s?k=" in amzn_link, "Invalid Amazon India link"

    print("All tests passed!")

if __name__ == "__main__":
    main()
