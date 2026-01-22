from ibookr.helpers.image_helper import batch_process_input_images
from ibookr.helpers.agent_helper import extract_book_data_from_image_file
from ibookr.helpers.input_helper import process_json_input
from ibookr.helpers.search_helper import batch_fill
from ibookr.helpers.output_helper import output_to_markdown

from ibookr.settings import settings

from pathlib import Path
import json
import os
import datetime
import logging
import schedule
import time
import signal
import shutil

logger = logging.getLogger(__name__)


def image_to_json_task(
    image_input_folder_path: str,
    image_preprocessed_folder_path: str,
    image_archive_folder_path: str,
    json_output_folder_path: str,
    image_error_folder_path: str,
    resize_width: int = 800,
):
    """Process images in the input folder to extract book data and save as JSON files in the output folder."""
    try:
        # Step 1: Batch process input images (convert and resize)
        batch_process_input_images(
            input_folder_path=image_input_folder_path,
            output_folder_path=image_preprocessed_folder_path,
            resize_width=resize_width,
        )

        # Step 2: Process each PNG image in the output folder
        preprocessed_folder = Path(image_preprocessed_folder_path)
        png_files = set(preprocessed_folder.glob("*.png"))
        png_files.update(preprocessed_folder.glob("*.PNG"))

        for png_file in png_files:
            logger.info(f"Extracting book data from image: {png_file.name}")

            try:
                # Extract book data using the agent
                book_data_results = extract_book_data_from_image_file(png_file)

                # Save extracted data to JSON file
                output_folder = Path(json_output_folder_path)
                output_folder.mkdir(parents=True, exist_ok=True)
                json_output_path = output_folder / png_file.with_suffix(".json").name
                with open(json_output_path, "w", encoding="utf-8") as json_file:
                    json.dump(
                        [result.model_dump() for result in book_data_results],
                        json_file,
                        ensure_ascii=False,
                        indent=4,
                    )
                # move the processed image to archive folder
                archive_folder = Path(image_archive_folder_path)
                archive_folder.mkdir(parents=True, exist_ok=True)
                png_file.rename(archive_folder / png_file.name)
            except Exception as e:
                logger.error(f"Error processing image file {png_file.name}: {e}")
                # move png file to error folder
                error_folder = Path(image_error_folder_path)
                error_folder.mkdir(parents=True, exist_ok=True)
                png_file.rename(error_folder / png_file.name)

    except Exception as e:
        logger.error(f"Error in image to JSON task: {e}")


def process_single_json_file_task(
    json_input_folder: str,
    json_output_folder: str,
    json_book_output_folder: str,
    json_error_folder: str,
):
    logger.info("Starting processing of input files.")

    # list all .json files in the input folder
    # for each file, call process_json_input function
    for filename in os.listdir(json_input_folder):
        if filename.endswith(".json"):
            logger.info(f"Processing file: {filename}")

            file_path = os.path.join(json_input_folder, filename)
            book_input_list = process_json_input(file_path)

            if not book_input_list or len(book_input_list) == 0:
                # move to error folder
                shutil.move(file_path, os.path.join(json_error_folder, filename))
                return

            filled_count = batch_fill(book_input_list)
            if filled_count == 0:
                # move to error folder
                shutil.move(file_path, os.path.join(json_error_folder, filename))
                return

            # Add timestamp as postfix to output file
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = filename.replace(".json", f"_{timestamp}.csv")

            output_success = output_to_markdown(
                book_input_list, json_book_output_folder
            )

            if not output_success:
                # move to error folder
                shutil.move(file_path, os.path.join(json_error_folder, filename))
                return

            logger.info(
                f"Successfully processed {filename}: Filled ISBNs for {filled_count} books."
            )
            # move to output folder
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = filename.replace(".json", f"_{timestamp}.json")
            shutil.move(file_path, os.path.join(json_output_folder, output_filename))
            return


def _run_tasks_once():
    image_to_json_task(
        image_input_folder_path=settings.image_to_json_input_folder,
        image_preprocessed_folder_path=settings.image_to_json_preprocessed_folder,
        image_archive_folder_path=settings.image_to_json_archive_folder,
        json_output_folder_path=settings.image_to_json_output_folder,
        image_error_folder_path=settings.image_to_json_error_folder,
        resize_width=settings.image_to_json_resize_width,
    )
    process_single_json_file_task(
        json_input_folder=settings.json_input_folder,
        json_output_folder=settings.json_output_folder,
        json_book_output_folder=settings.json_book_output_folder,
        json_error_folder=settings.json_error_folder,
    )


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        print("Received termination signal. Exiting gracefully...")
        self.kill_now = True


def main():
    # create necessary folders
    Path(settings.image_to_json_input_folder).mkdir(parents=True, exist_ok=True)
    Path(settings.image_to_json_preprocessed_folder).mkdir(parents=True, exist_ok=True)
    Path(settings.image_to_json_output_folder).mkdir(parents=True, exist_ok=True)
    Path(settings.image_to_json_error_folder).mkdir(parents=True, exist_ok=True)
    Path(settings.json_input_folder).mkdir(parents=True, exist_ok=True)
    Path(settings.json_output_folder).mkdir(parents=True, exist_ok=True)
    Path(settings.json_book_output_folder).mkdir(parents=True, exist_ok=True)
    Path(settings.json_error_folder).mkdir(parents=True, exist_ok=True)

    if settings.run_mode == "once":
        _run_tasks_once()
    elif settings.run_mode == "scheduler":
        logger.info(
            f"Starting scheduler with interval {settings.scheduler_interval_minutes} minutes."
        )
        killer = GracefulKiller()
        schedule.every(settings.scheduler_interval_minutes).minutes.do(_run_tasks_once)
        while not killer.kill_now:
            schedule.run_pending()
            time.sleep(10)
    else:
        logger.error(f"Invalid run mode: {settings.run_mode}")
