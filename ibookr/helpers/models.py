from pydantic import BaseModel
import datetime
from pathlib import Path


class ImageToBookResult(BaseModel):
    title: str = None
    author: str = None


class Book(BaseModel):
    title: str = None
    series: str = None
    seriesNo: float = None
    author: str = None
    categories: list[str] = []
    tags: list[str] = []
    subjects: list[str] = []
    persons: list[str] = []
    places: list[str] = []
    times: list[str] = []
    publisher: str = None
    first_publish_year: str = None
    page_count: int = None
    isbn: str = None
    cover_image_url: str = None
    local_cover_image_url: str = None

    def to_markdown_file(self, output_folder_path: str):
        now_formatted = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        author_name_escaped = (
            "".join(c for c in self.author if c.isalnum() or c.isspace())
            .rstrip()
            .lower()
        )
        if not author_name_escaped:
            author_name_escaped = "unknown_author"

        file_name_escaped = (
            "".join(c for c in self.title if c.isalnum() or c.isspace())
            .rstrip()
            .lower()
        )
        if not file_name_escaped:
            file_name_escaped = (
                f"unknown_{now_formatted.replace(' ', '_').replace(':', '')}"
            )

        folder_path = f"{output_folder_path}/{author_name_escaped}"
        Path(folder_path).mkdir(parents=True, exist_ok=True)

        file_path = f"{folder_path}/{file_name_escaped}.md"

        # check if file already exists
        # if it does, increment a counter until we find a free name
        counter = 1
        while Path(file_path).exists():
            file_path = f"{folder_path}/{file_name_escaped}_{counter}.md"
            counter += 1

        with open(file_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"title: {self.title or ''}\n")
            f.write(f"series: {self.series or ''}\n")
            f.write(f"seriesNo: {self.seriesNo or ''}\n")
            f.write(f"author: {self.author or ''}\n")
            f.write("categories:\n")
            for cat in self.categories or []:
                f.write(f"  - {cat}\n")

            f.write("tags:\n")
            for tag in self.tags or []:
                f.write(f"  - {tag}\n")
            # always add 'Book' tag
            if "Book" not in (self.tags or []):
                f.write("  - Book\n")

            f.write("subjects:\n")
            for subj in self.subjects or []:
                f.write(f"  - {subj}\n")
            f.write("persons:\n")
            for person in self.persons or []:
                f.write(f"  - {person}\n")
            f.write("places:\n")
            for place in self.places or []:
                f.write(f"  - {place}\n")
            f.write("times:\n")
            for time in self.times or []:
                f.write(f"  - {time}\n")
            f.write(f"publisher: {self.publisher or ''}\n")
            f.write(f"firstPublishYear: {self.first_publish_year or ''}\n")
            f.write(f"pageCount: {self.page_count or ''}\n")
            f.write(f'isbn: "{self.isbn or ""}"\n')
            f.write(f"coverImageUrl: {self.cover_image_url or ''}\n")
            f.write(f"localCoverImageUrl: {self.local_cover_image_url or ''}\n")
            f.write(f"created: {now_formatted}\n")
            f.write("status: AUTOGEN\n")
            f.write("---\n\n")
            f.write(f"# {self.title or ''}\n\n")
