ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV log_file_path="/data/logs/ibookr.log"

ENV image_to_json_input_folder="/data/image_input"
ENV image_to_json_preprocessed_folder="/data/image_preprocessed"
ENV image_to_json_output_folder="/data/json_input"
ENV image_to_json_error_folder="/data/image_error"
ENV image_to_json_resize_width=1600
ENV image_to_json_archive_folder="/data/image_archive"

ENV json_input_folder="/data/json_input"
ENV json_output_folder="/data/json_output"
ENV json_book_output_folder="/data/json_book_output"
ENV json_error_folder="/data/json_error"

ENV openrouter_model_name="google/gemini-2.5-flash"
ENV openrouter_api_key=""

ENTRYPOINT ["python3", "main.py"]