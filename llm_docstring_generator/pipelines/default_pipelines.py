import os

from llm_docstring_generator.annotator.code_annotator import (
    DebugAnnotator,
    DefaultAnnotator,
)
from llm_docstring_generator.annotator.metadata_provider import (
    DebugMetaDataProvider,
    DefaultMetaDataProvider,
)
from llm_docstring_generator.llm.llm import DebugLLM, LocalTGILLM, OpenAILLM
from llm_docstring_generator.llm.llm_config import LLMConfig
from llm_docstring_generator.pipelines.code_annotation_pipeline import (
    CodeAnnotationPipeline,
)
from llm_docstring_generator.sorters.sort_python_files import (
    sort_python_files_by_imports,
)
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.copy_repository import (
    CopyRepositoryWithLLMDocstrings,
)


def debug_format(config: BaseConfig, llm_config: LLMConfig) -> CodeAnnotationPipeline:
    # assert sanity check to prevent the user accidentally using the wrong pipeline
    assert (
        llm_config.model == "debug"
    ), f"Model name should be 'debug' when using the debug pipeline, got {llm_config.model}."
    annotator = DebugAnnotator(
        llm=DebugLLM(config=llm_config),
        metadata_provider_class=DebugMetaDataProvider,
    )
    copy_repository = CopyRepositoryWithLLMDocstrings(
        original_repo_path=config.repository_path,
        new_repository_path=config.new_repository_path,  # type: ignore
    )

    return CodeAnnotationPipeline(
        annotator=annotator,
        copy_repository=copy_repository,
        config=config,
        sort_python_files_function=sort_python_files_by_imports,
    )


def tgi_local_format(
    config: BaseConfig, llm_config: LLMConfig
) -> CodeAnnotationPipeline:
    assert "TGI_MODEL_URL" in os.environ, "TGI_MODEL_URL not set"

    annotator = DefaultAnnotator(
        llm=LocalTGILLM(config=llm_config),
        metadata_provider_class=DefaultMetaDataProvider,
    )
    copy_repository = CopyRepositoryWithLLMDocstrings(
        original_repo_path=config.repository_path,
        new_repository_path=config.new_repository_path,  # type: ignore
    )

    return CodeAnnotationPipeline(
        annotator=annotator,
        copy_repository=copy_repository,
        config=config,
        sort_python_files_function=sort_python_files_by_imports,
    )


def gpt_format(config: BaseConfig, llm_config: LLMConfig) -> CodeAnnotationPipeline:
    assert "OPENAI_API_KEY" in os.environ, "OPENAI_API_KEY not set"
    if llm_config.model == "tgi":
        assert "OPENAI_API_URL" in os.environ, "OPENAI_API_URL needs to be set"

    annotator = DefaultAnnotator(
        llm=OpenAILLM(config=llm_config),
        metadata_provider_class=DefaultMetaDataProvider,
    )
    copy_repository = CopyRepositoryWithLLMDocstrings(
        original_repo_path=config.repository_path,
        new_repository_path=config.new_repository_path,  # type: ignore
    )

    return CodeAnnotationPipeline(
        annotator=annotator,
        copy_repository=copy_repository,
        config=config,
        sort_python_files_function=sort_python_files_by_imports,
    )


pipeline_factory = dict()
# you can add more formats here
pipeline_factory["debug"] = debug_format
pipeline_factory["tgi-local"] = tgi_local_format
pipeline_factory["tgi"] = gpt_format
pipeline_factory["openai-gpt"] = gpt_format
# explicit model names, shortcut
pipeline_factory["gpt-3.5-turbo"] = gpt_format
pipeline_factory["gpt-4-0125-preview"] = gpt_format
pipeline_factory["gpt-4-turbo"] = gpt_format
