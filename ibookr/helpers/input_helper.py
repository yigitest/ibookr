import json
import logging
from typing import List

from .models import Book

logger = logging.getLogger(__name__)


def _parse_json_input(json_data: list) -> List[Book]:
    return [Book(**item) for item in json_data]


def process_json_input(file_path: str) -> List[Book]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            result = _parse_json_input(data)
            return result
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading JSON input file {file_path}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error processing file {file_path}: {e}")
        return []
