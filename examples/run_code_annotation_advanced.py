"""
Example how to customize the pipeline.
"""
from pathlib import Path
from typing import List

import dotenv
from llm_docstring_generator import (
    DEFAULT_DATA_DIR,
    DEFAULT_DOCSTRING_SYSTEM_PROMPT,
    run_code_annotation_pipeline,
)
from llm_docstring_generator.annotator.code_annotator import DefaultAnnotator
from llm_docstring_generator.annotator.metadata_provider import NoMetaDataProvider
from llm_docstring_generator.llm.llm import OpenAILLM
from llm_docstring_generator.llm.llm_config import LLMConfig
from llm_docstring_generator.pipelines.code_annotation_pipeline import (
    CodeAnnotationPipeline,
)
from llm_docstring_generator.pipelines.default_pipelines import pipeline_factory
from llm_docstring_generator.python_files.python_file import PythonFile
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.copy_repository import CopyRepositoryWithLLMComments


def filter_python_files(python_files: List[PythonFile]) -> List[PythonFile]:
    """
    Filters the python files to only include files from optuna root folder (i.e. no tests, examples, etc.)
    """
    python_files = [
        python_file
        for python_file in python_files
        if python_file.import_name.startswith("optuna")
    ]
    return python_files


def my_baseline_pipeline(
    config: BaseConfig, llm_config: LLMConfig
) -> CodeAnnotationPipeline:
    """
    Custom pipeline that only annotates functions and classes.
    Does not use metainformation from previous annotations.
    Useful for comparing the performance w.r.t. the original pipeline.
    """
    annotator = DefaultAnnotator(
        llm=OpenAILLM(config=llm_config),
        metadata_provider_class=NoMetaDataProvider,  # no metadata about previous annotations
    )
    # As an example how to customize the pipeline,
    # we add the llm annotations as code comments instead of docstrings
    copy_repository = CopyRepositoryWithLLMComments(
        original_repo_path=config.repository_path,
        new_repository_path=config.new_repository_path,  # type: ignore
    )

    return CodeAnnotationPipeline(
        annotator=annotator,
        copy_repository=copy_repository,
        filter_python_files_function=filter_python_files,
        config=config,
        sort_python_files_function=lambda x: x,  # no need to sort the files
    )


# Add the pipeline to the factory and use the name in the run_code_annotation_pipeline function
pipeline_factory["my_baseline_pipeline"] = my_baseline_pipeline

if __name__ == "__main__":
    if (DEFAULT_DATA_DIR / ".env").exists():
        dotenv.load_dotenv(DEFAULT_DATA_DIR / ".env")

    run_code_annotation_pipeline(
        repository_name="optuna",
        remote_url="git@github.com:optuna/optuna.git",
        system_prompt=DEFAULT_DOCSTRING_SYSTEM_PROMPT,
        model="gpt-4-0125-preview",
        max_prompt_token_length=2048,
        pipeline_name="my_baseline_pipeline",
        new_repository_path=Path(__file__).parent.parent / "data" / "optuna_annotated",
    )
