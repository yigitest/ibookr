from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import logging


def setup_logging():
    # Remove all handlers associated with the root logger to prevent duplicate logs
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(filename)s/%(funcName)s - %(message)s"
    )

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create file handler
    if settings.log_file_path:
        # create folder if it doesn't exist
        os.makedirs(os.path.dirname(settings.log_file_path), exist_ok=True)

        file_handler = logging.FileHandler(settings.log_file_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


class Settings(BaseSettings):
    app_name: str = "iBookr"
    app_version: str = "0.9.9"
    app_url: str = "https://ibookr.iz0.top"
    app_contact_email: str = "ibookr@iz0.top"

    run_mode: str = "scheduler"  # options: "once", "scheduler"
    scheduler_interval_minutes: int = 10

    # API rate limit settings (sleep time between requests)
    book_search_rate_limit_seconds: int = 2

    log_file_path: str = ""

    debug: bool = False

    image_to_json_input_folder: str = "temp/image_input"
    image_to_json_preprocessed_folder: str = "temp/image_preprocessed"
    image_to_json_output_folder: str = "temp/json_input"
    image_to_json_error_folder: str = "temp/image_error"
    image_to_json_resize_width: int = 1600
    image_to_json_archive_folder: str = "temp/image_archive"

    json_input_folder: str = "temp/json_input"
    json_output_folder: str = "temp/json_output"
    json_book_output_folder: str = "temp/json_book_output"
    json_error_folder: str = "temp/json_error"

    # openrouter_model_name: str = "nvidia/nemotron-nano-12b-v2-vl:free"
    openrouter_model_name: str = "google/gemini-2.5-flash"
    openrouter_api_key: str = ""

    book_data_extractor_system_prompt: str = (
        "Analyze the provided image of a bookshelf. Identify every book visible."
        "Extract the author and title for each book. Return book data as a JSON array.\n"
        "Constraints:\n"
        "    If a field is illegible, leave it empty.\n"
        "    Do not translate book titles.\n"
        "    No conversational text; output raw JSON text only.\n"
        "Fields:\n"
        "    title: Title of the book.\n"
        "    author: Author name. No special characters."
    )

    model_config = SettingsConfigDict(
        cli_parse_args=True, env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
setup_logging()
