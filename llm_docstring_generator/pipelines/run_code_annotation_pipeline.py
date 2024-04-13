from pathlib import Path
from typing import Optional

from llm_docstring_generator.llm.llm_config import LLMConfig
from llm_docstring_generator.llm.prompts import DEFAULT_DOCSTRING_SYSTEM_PROMPT
from llm_docstring_generator.pipelines.code_annotation_pipeline import (
    CodeAnnotationPipeline,
)
from llm_docstring_generator.pipelines.default_pipelines import pipeline_factory
from llm_docstring_generator.utils.base_config import BaseConfig
from loguru import logger


def run_code_annotation_pipeline(
    repository_name: str,
    remote_url: Optional[str] = None,
    repository_path: Optional[Path | str] = None,
    new_repository_path: Optional[Path | str] = None,
    cache_path: Optional[Path | str] = None,
    system_prompt: str = DEFAULT_DOCSTRING_SYSTEM_PROMPT,
    model: str = "gpt-4-0125-preview",
    max_prompt_token_length: int = 2048,
    pipeline_name: Optional[str] = None,
):
    """
    Run the code annotation pipeline
    :param repository_name: The name of the repository to be annotated.
    The repository should contain this name in the root path, e.g. transformers/transformers
    :param remote_url: If you want to clone a remote repository, set the remote_url
    :param repository_path: If you want to use a local repository, set the local_repository_path
    :param new_repository_path: The path where the annotated repository will be saved
    :param cache_path: The cache directory. This is where the annotated repository will be saved
    :param system_prompt: System prompt to be used for the LLM
    :param model: The LLM model to be used
    :param max_prompt_token_length: The maximum token length for the prompt, excluding the system prompt
    :param pipeline_name: Name of the pipeline to be used, defaults to the model name if not set.
                          Useful when using arbitrary openai models together with openai-gpt pipeline.
                          Can also be used to call custom pipelines that where added to the pipeline_factory.
    :return: Annotated python files
    """
    pipeline_name = pipeline_name or model
    assert pipeline_name in pipeline_factory, (
        f"Pipeline {pipeline_name} not found. "
        f"Available pipelines: {pipeline_factory.keys()}. "
        f"Please use an available pipeline or add a custom one "
        f"(see run_code_annotation_advanced.py example)"
    )

    config = BaseConfig(
        repository_name=repository_name,
        repository_path=repository_path,  # type: ignore[arg-type]
        remote_url=remote_url,
        cache_path=cache_path,  # type: ignore[arg-type]
        new_repository_path=new_repository_path,  # type: ignore[arg-type]
    )
    llm_config = LLMConfig(
        system_prompt=system_prompt,
        model=model,
        db_root_path=config.cache_path,
        max_prompt_token_length=max_prompt_token_length,
    )
    code_annotation_pipeline: CodeAnnotationPipeline = pipeline_factory[pipeline_name](
        config, llm_config
    )
    python_files = code_annotation_pipeline.run()
    logger.info(f"Annotated {len(python_files)} python files")
    return python_files
