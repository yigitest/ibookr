from PIL import Image
from pathlib import Path
from heic2png import HEIC2PNG

import logging

logger = logging.getLogger(__name__)


def _convert_heic_files_to_png(input_folder: Path, output_folder: Path):
    """Convert all HEIC files in the input folder to PNG format.
    The original HEIC files are deleted after conversion."""

    output_folder.mkdir(parents=True, exist_ok=True)

    input_files = list(input_folder.glob("*.heic"))
    input_files.extend(list(input_folder.glob("*.HEIC")))

    for heic_file in input_files:
        logger.info(f"Processing image: {heic_file.name}")
        heic_img = HEIC2PNG(heic_file, quality=90)
        output_file_path = output_folder / (heic_file.stem + ".png")
        heic_img.save(output_file_path, ".png")
        logger.info(
            f"Converted HEIC to PNG: {heic_file.name} -> {output_file_path.name}"
        )
        heic_file.unlink()  # Remove the original HEIC file


def _convert_jpeg_files_to_png(input_folder: Path, output_folder: Path):
    """Convert all JPEG files in the input folder to PNG format.
    The original JPEG files are deleted after conversion."""

    output_folder.mkdir(parents=True, exist_ok=True)

    input_files = set(input_folder.glob("*.jpg"))
    input_files.update(input_folder.glob("*.jpeg"))
    input_files.update(input_folder.glob("*.JPG"))
    input_files.update(input_folder.glob("*.JPEG"))

    for jpeg_file in input_files:
        logger.info(f"Processing image: {jpeg_file.name}")
        with Image.open(jpeg_file) as img:
            output_file_path = output_folder / (jpeg_file.stem + ".png")
            img.save(output_file_path, "PNG")
            logger.info(
                f"Converted JPEG to PNG: {jpeg_file.name} -> {output_file_path.name}"
            )
        jpeg_file.unlink()  # Remove the original JPEG file


def _resize_and_move_png_images(
    input_folder: Path,
    output_folder: Path,
    resize_width: int,
):
    """Resize all PNG images in the input folder to the specified width
    while maintaining aspect ratio."""

    output_folder.mkdir(parents=True, exist_ok=True)

    input_files = set(input_folder.glob("*.png"))
    input_files.update(input_folder.glob("*.PNG"))

    for png_file in input_files:
        logger.info(f"Processing image: {png_file.name}")

        output_file_path = output_folder / png_file.name
        resized = False
        with Image.open(png_file) as img:
            if resize_width > 0 and img.width > resize_width:
                # Resize image while maintaining aspect ratio
                img = img.resize(
                    (
                        resize_width,
                        int(img.height * resize_width / img.width),
                    ),
                    Image.LANCZOS,
                )

                img.save(output_file_path, "PNG")
                resized = True
                logger.info(
                    f"Resized image: {png_file.name} -> {output_file_path.name}"
                )
        if resized:
            png_file.unlink()  # Remove the original PNG file
        else:
            # If no resizing was done, just move the file
            output_file_path = output_folder / png_file.name
            png_file.rename(output_file_path)
            logger.info(f"Moved image without resizing: {png_file.name}")


def batch_process_input_images(
    input_folder_path: str,
    output_folder_path: str,
    resize_width: int,
):
    """Process all input images: convert HEIC and JPEG to PNG and resize PNG images."""

    try:
        _convert_heic_files_to_png(
            input_folder=Path(input_folder_path),
            output_folder=Path(input_folder_path),
        )

        _convert_jpeg_files_to_png(
            input_folder=Path(input_folder_path),
            output_folder=Path(input_folder_path),
        )

        _resize_and_move_png_images(
            input_folder=Path(input_folder_path),
            output_folder=Path(output_folder_path),
            resize_width=resize_width,
        )

    except Exception as e:
        logger.error(f"Error processing input images: {e}")

    logger.info("Input image processing completed.")
