# ibookr

## docker deployment guide

Create .env file with at least this variables:

```
APP_UID=1000
APP_GID=1000
DATA_VOLUME=/path/to/data/volume
OPENROUTER_API_KEY=your-openrouter-key
```

Or you can be more specific:

```
log_file_path="/data/logs/ibookr.log"
image_to_json_input_folder="/data/image_input"
image_to_json_preprocessed_folder="/data/image_preprocessed"
image_to_json_output_folder="/data/json_input"
image_to_json_error_folder="/data/image_error"
image_to_json_resize_width=1600
image_to_json_archive_folder="/data/image_archive"
json_input_folder="/data/json_input"
json_output_folder="/data/json_output"
json_book_output_folder="/data/json_book_output"
json_error_folder="/data/json_error"
openrouter_model_name="google/gemini-2.5-flash"
openrouter_api_key=""
```


