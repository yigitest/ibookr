
# ibookr

**ibookr** uses AI services to extract author and book titles from single or batch bookshelf photos. It enriches this data with ISBN, thumbnails, topics, time, and place info using Google Books and OpenLibrary APIs. All results are saved as Markdown files (see examples/).

I use these files in Obsidian to create a personal book database ("bases").


## Quick Start with Docker

Before you begin, create an OpenRouter account and generate an API key.

You can find example settings in the .env_example file. Adjust the .env and docker-compose.yml files to fit your needs.

In short:
- Copy .env_example to .env and update the values as needed.
- Review docker-compose.yml and update folder paths and settings for your environment.
- Add your OpenRouter API key to the .env file.
- Then start the project using Docker.

## License

[MIT](https://choosealicense.com/licenses/mit/)