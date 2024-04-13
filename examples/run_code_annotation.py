import sys
from pathlib import Path

import dotenv
from llm_docstring_generator import (
    DEFAULT_DATA_DIR,
    DEFAULT_DOCSTRING_SYSTEM_PROMPT,
    run_code_annotation_pipeline,
)
from loguru import logger

if __name__ == "__main__":
    # remove these two lines if you want to see debug logs, such as import dependencies
    # and which prompts are cached etc.
    logger.remove(0)
    logger.add(sys.stderr, level="INFO")

    # You can store secrets in .env file, e.g. OPENAI_API_KEY
    if (DEFAULT_DATA_DIR / ".env").exists():
        dotenv.load_dotenv(DEFAULT_DATA_DIR / ".env")
        logger.info("Loaded .env file")

    run_code_annotation_pipeline(
        repository_name="llm_docstring_generator",
        remote_url="git@github.com:maxjeblick/llm-docstring-generator.git",
        system_prompt=DEFAULT_DOCSTRING_SYSTEM_PROMPT,
        model="gpt-4-turbo",  # use "debug" for testing/debugging
        max_prompt_token_length=2048,
        new_repository_path=Path(__file__).parent.parent
        / "data"
        / "llm_docstring_generator_annotated",
    )
