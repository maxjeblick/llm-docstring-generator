import ast
from pathlib import Path

import pytest
from faker import Faker
from llm_docstring_generator.parser.load_python_files import load_python_files
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.copy_repository import (
    CopyRepositoryWithLLMComments,
    CopyRepositoryWithLLMDocstrings,
)


@pytest.fixture(scope="function")
def python_files(tmp_path):
    fake = Faker()
    root_path = Path(__file__).parent.parent.parent
    repository_path = root_path / "llm_docstring_generator"
    assert repository_path.exists(), f"{repository_path} does not exist"
    config = BaseConfig(
        repository_name="llm_docstring_generator",
        repository_path=repository_path,
        remote_url="",
        cache_path=root_path,
    )
    python_files = load_python_files(config)
    assert len(python_files) >= 25, f"len(python_files): {len(python_files)}"
    for python_file in python_files:
        python_file.llm_response = fake.paragraph()
        for function in python_file.functions:
            function.llm_response = fake.paragraph() + "\n\n" + fake.paragraph()
        for class_ in python_file.classes:
            class_.llm_response = fake.paragraph() + "\n\n" + fake.paragraph()
            for function in class_.methods:
                function.llm_response = fake.paragraph()
    return python_files


def test_copy_repository_with_llm_comments(python_files, tmp_path):
    copy_repository = CopyRepositoryWithLLMComments(
        original_repo_path=tmp_path / "llm_docstring_generator",
        new_repository_path=tmp_path,
    )
    run_insert_llm_annotation_test(python_files, copy_repository)


def test_copy_repository_with_llm_docstrings(python_files, tmp_path):
    copy_repository = CopyRepositoryWithLLMDocstrings(
        original_repo_path=tmp_path / "llm_docstring_generator",
        new_repository_path=tmp_path,
    )
    run_insert_llm_annotation_test(python_files, copy_repository)


def run_insert_llm_annotation_test(python_files, copy_repository):
    for python_file in python_files:
        python_file.llm_response = "LLM Annotation Test" + python_file.llm_response
        codestring = copy_repository.add_llm_annotations_to_codestring(python_file)
        try:
            ast.parse(codestring)
        except Exception as e:
            raise ValueError(f"Failed to parse codestring: {codestring}") from e
        assert python_file.llm_response[:30] in codestring, codestring
        assert "LLM Annotation Test" in codestring, codestring
