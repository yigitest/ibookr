import time
import requests

import logging

from .models import Book
from ibookr.settings import settings

logger = logging.getLogger(__name__)


def fill_info_from_openlibrary(book: Book) -> bool:
    search_url = "https://openlibrary.org/search.json"
    params = {
        "author": book.author,
        "title": book.title,
        "fields": "title,author_name,first_publish_year,isbn,subject,person,place,time",
    }
    headers = {
        "User-Agent": f"{settings.app_name}/{settings.app_version} ({settings.app_contact_email})"
    }
    try:
        response = requests.get(search_url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        docs = data.get("docs", [])
        if docs:
            first_book = docs[0]
            book.first_publish_year = first_book.get("first_publish_year", None)
            book.isbn = (
                first_book.get("isbn", [None])[0] if first_book.get("isbn") else None
            )
            book.subjects = first_book.get("subject", [])
            book.persons = first_book.get("person", [])
            book.places = first_book.get("place", [])
            book.times = first_book.get("time", [])
        else:
            logger.debug(f"No book data found for {book.author} - {book.title}")
            return False
    except requests.RequestException as e:
        logger.warning(f"Error fetching book data: {e}")
        return False
    return True


def fill_info_from_googlebooks(
    book: Book, title_override: str = None, author_override: str = None
) -> bool:
    search_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"intitle:{title_override or book.title}+inauthor:{author_override or book.author}",
    }
    headers = {
        "User-Agent": f"{settings.app_name}/{settings.app_version} ({settings.app_contact_email})"
    }
    try:
        response = requests.get(search_url, params=params, headers=headers)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])
        for item in items:
            volume_info = item.get("volumeInfo", {})
            identifiers = volume_info.get("industryIdentifiers", [])
            for identifier in identifiers:
                if identifier.get("type") in ["ISBN_10", "ISBN_13"]:
                    isbn = identifier.get("identifier")
                    book.isbn = isbn

                    # found valid ISBN
                    # fill categories for this book as well
                    for category in volume_info.get("categories", []):
                        if category not in book.categories:
                            book.categories.append(category)

                    book.cover_image_url = volume_info.get("imageLinks", {}).get(
                        "thumbnail", None
                    )

                    return True

    except requests.RequestException as e:
        logger.warning(f"Error fetching book data: {e}")
        return False

    return False


def fill_book_info(book_input: Book) -> bool:
    result = fill_info_from_openlibrary(book_input)
    if not result:
        logger.warning(
            f"OpenLibrary search failed for {book_input.author} - {book_input.title}"
        )

    result = fill_info_from_googlebooks(book_input)
    if result:
        return True
    else:
        logger.warning(
            f"Google Books search failed for {book_input.author} - {book_input.title}"
        )

        # split book title by space and special characters
        # try googlebooks search again by reducing the length of the title progressively
        # first 5 words, then 4, then 3, then 2, then 1
        # delete from the beginning
        title_words = book_input.title.split()
        for i in range(len(title_words) - 1, 0, -1):
            reduced_title = " ".join(title_words[-i:])
            logger.info(f"Trying reduced title search: '{reduced_title}'")
            result = fill_info_from_googlebooks(
                book_input, reduced_title, book_input.author
            )
            if result:
                return True

        # same thing for author name:
        author_parts = book_input.author.split()
        for i in range(len(author_parts) - 1, 0, -1):
            reduced_author = " ".join(author_parts[i:])
            logger.info(f"Trying reduced author search: '{reduced_author}'")
            result = fill_info_from_googlebooks(
                book_input, book_input.title, reduced_author
            )
            if result:
                return True

    logger.warning(f"Could not find ISBN for {book_input.author} - {book_input.title}")
    return False


def batch_fill(book_inputs: list[Book]) -> int:
    logger.info(f"Starting batch ISBN filling process for {len(book_inputs)} books.")
    try:
        filled_count = 0
        for book_input in book_inputs:
            if fill_book_info(book_input):
                filled_count += 1
            time.sleep(
                settings.book_search_rate_limit_seconds
            )  # To respect API rate limits
    except Exception as e:
        logger.error(f"Error during batch filling process: {e}")
        return 0
    logger.info(
        f"Completed batch ISBN filling process. Filled ISBNs for {filled_count} books out of {len(book_inputs)}."
    )
    return filled_count
