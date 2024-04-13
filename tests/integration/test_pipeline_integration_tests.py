from typing import Union

import pytest
from llm_docstring_generator import run_code_annotation_pipeline
from llm_docstring_generator.annotator.code_annotator import DefaultAnnotator
from llm_docstring_generator.annotator.metadata_provider import (
    BaseMetaDataProvider,
    DefaultMetaDataProvider,
    get_functions_and_classes_used,
)
from llm_docstring_generator.llm.llm import DebugLLM
from llm_docstring_generator.pipelines.code_annotation_pipeline import (
    CodeAnnotationPipeline,
)
from llm_docstring_generator.pipelines.default_pipelines import pipeline_factory
from llm_docstring_generator.python_files.function_and_classes import (
    Class,
    CodeObject,
    Function,
)
from llm_docstring_generator.python_files.python_file import PythonFile
from llm_docstring_generator.sorters.sort_python_files import (
    sort_python_files_by_imports,
)
from llm_docstring_generator.utils.copy_repository import (
    CopyRepositoryWithLLMDocstrings,
)


class AssertMetaDataProvider(BaseMetaDataProvider):
    num_failures: int = 0
    total_calls: int = 0

    def error_message(self, function: CodeObject, function_or_class: CodeObject):
        return f"Error in {function.complete_import_name} Function depends on {function_or_class.complete_import_name}. "

    def get_function_metadata(self, function: Union[Function | Class]) -> str:
        functions_used = get_functions_and_classes_used(
            code_object=function, python_files=self.python_files
        )
        self.total_calls += len(functions_used)
        for function_or_class in functions_used:
            if function_or_class.llm_response == "":
                self.num_failures += 1
            elif isinstance(function_or_class, Class):
                for method in function_or_class.methods:
                    if method.llm_response == "":
                        self.num_failures += 1

        # allow for some parser errors as code may not always have a well defined structure
        if self.num_failures > 60 and self.num_failures / (self.total_calls + 1) > 0.25:
            raise ValueError(
                f"Too many failures {self.num_failures} {self.total_calls}"
            )

        return "Debug Annotation"

    def get_class_metadata(self, class_: Class) -> str:
        for method in class_.methods:
            self.get_function_metadata(method)
        return ""

    def get_python_file_metadata(self, python_file: PythonFile) -> str:
        return ""


def filter_python_files(python_files):
    python_files = [
        python_file
        for python_file in python_files
        if any(
            [
                python_file.import_name.startswith("optuna"),
                python_file.import_name.startswith("haystack"),
            ]
        )
    ]
    return python_files


def integration_test_format(config, llm_config):
    annotator = DefaultAnnotator(
        llm=DebugLLM(config=llm_config),
        metadata_provider_class=DefaultMetaDataProvider,
    )
    copy_repository = CopyRepositoryWithLLMDocstrings(
        original_repo_path=config.repository_path,
        new_repository_path=config.new_repository_path,  # type: ignore
    )

    return CodeAnnotationPipeline(
        config=config,
        annotator=annotator,
        copy_repository=copy_repository,
        filter_python_files_function=filter_python_files,
        sort_python_files_function=sort_python_files_by_imports,
    )


pipeline_factory["integration_test"] = integration_test_format


@pytest.mark.parametrize(
    "repository_name, remote_url",
    [
        (
            "optuna",
            "https://github.com/optuna/optuna.git",
        ),
        (
            "haystack",
            "https://github.com/deepset-ai/haystack.git",
        ),
    ],
)
def test_pipeline(
    tmp_path,
    repository_name,
    remote_url,
):
    python_files = run_code_annotation_pipeline(
        cache_path=tmp_path,
        repository_name=repository_name,
        remote_url=remote_url,
        model="integration_test",
    )
    for python_file in python_files:
        if python_file.codestring == "":
            continue

        for function in python_file.functions:
            assert function.llm_response != "", python_file.import_name
        for cls in python_file.classes:
            assert cls.llm_response != "", python_file.import_name
            for method in cls.methods:
                assert method.llm_response != "", python_file.import_name
