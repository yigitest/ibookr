import logging

from .models import Book


logger = logging.getLogger(__name__)


def output_to_markdown(books: list[Book], output_folder_path: str) -> bool:
    for book in books:
        book.to_markdown_file(output_folder_path)
    return True
