from ibookr.settings import settings
from .models import ImageToBookResult


from pydantic_ai import Agent, BinaryContent
from pydantic_ai.models.openrouter import OpenRouterModel
from pydantic_ai.providers.openrouter import OpenRouterProvider

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentHelper:
    _agent = None

    @staticmethod
    def get_agent():
        if AgentHelper._agent is None:
            logger.info("Initializing Book Data Extractor Agent...")
            logger.info(f"Using OpenRouter Model: {settings.openrouter_model_name}")
            model = OpenRouterModel(
                settings.openrouter_model_name,
                provider=OpenRouterProvider(
                    api_key=settings.openrouter_api_key,
                    app_url=settings.app_url,
                    app_title=settings.app_name,
                ),
            )
            AgentHelper._agent = Agent(
                model,
                output_type=list[ImageToBookResult],
                system_prompt=settings.book_data_extractor_system_prompt,
            )
        return AgentHelper._agent


def extract_book_data_from_image_file(image_file_path: Path) -> list[ImageToBookResult]:
    return extract_book_data_from_image(image_file_path.read_bytes(), "image/png")


def extract_book_data_from_image(
    image_data: bytes, image_mimetype: str = "image/png"
) -> list[ImageToBookResult]:
    agent = AgentHelper.get_agent()
    binary_content = BinaryContent(data=image_data, media_type=image_mimetype)
    result = agent.run_sync(
        [
            binary_content,
        ]
    )
    logger.info(f"AI Agent processed image data, Usage: {result.usage()}")
    return result.output
