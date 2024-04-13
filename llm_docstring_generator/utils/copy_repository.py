import shutil
from pathlib import Path
from typing import List, Union

from llm_docstring_generator.python_files.function_and_classes import (
    Class,
    CodeObject,
    Function,
)
from llm_docstring_generator.python_files.python_file import PythonFile
from loguru import logger


class CopyRepositoryBase:
    """
    Copies the repository to a new location.
    The CopyRepository class does not add any annotations to the code.
    Overwrite add_llm_annotations_to_codestring to add annotations.
    """

    def __init__(self, original_repo_path: Path, new_repository_path: Path):
        self.original_repo_path = original_repo_path
        self.new_repository_path = new_repository_path

    def __call__(self, python_files: List[PythonFile]) -> List[PythonFile]:
        for python_file in python_files:
            self.copy_python_file(python_file)
        logger.info(f"Saved python files to {self.new_repository_path}")
        self.copy_non_python_files()
        logger.info(f"Copied remaining (non .py) files to {self.new_repository_path}")
        # return python_files to be able to use in the pipeline
        return python_files

    def copy_python_file(self, python_file: PythonFile):
        codestring = self.add_llm_annotations_to_codestring(python_file)
        relative_filepath = python_file.import_name.replace(".", "/") + ".py"
        save_path = self.new_repository_path / relative_filepath
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with open(save_path, "w") as f:
            f.write(codestring)

    def add_llm_annotations_to_codestring(self, python_file: PythonFile) -> str:
        return python_file.codestring

    def copy_non_python_files(self):
        self.new_repository_path.mkdir(parents=True, exist_ok=True)
        venv_path = self.original_repo_path / "venv"
        env_path = self.original_repo_path / "env"

        for file in self.original_repo_path.glob("**/*"):
            if venv_path in file.parents or env_path in file.parents:
                continue

            if (
                file.is_file()
                and not (
                    self.new_repository_path / file.relative_to(self.original_repo_path)
                ).exists()
            ):
                new_file_path = self.new_repository_path / file.relative_to(
                    self.original_repo_path
                )
                new_file_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file, new_file_path)


def insert_elements(x: List, to_insert: List, start_line: int):
    """
    >>> x = [0, 1, 2, 3, 4, 5]
    >>> to_insert = ["a", "b", "c"]
    >>> start_line = 2
    >>> expected = [0, 1, "a", "b", "c", 2, 3, 4, 5]
    >>> insert_elements(x, to_insert, start_line)
    >>> x == expected
    True
    """
    for i, element in enumerate(to_insert):
        x.insert(start_line + i, element)


class CopyRepositoryWithLLMComments(CopyRepositoryBase):
    """
    This class adds annotations to the code in form of comments before the function/class definition.
    """

    def add_llm_annotations_to_codestring(self, python_file: PythonFile) -> str:
        functions_and_classes = python_file.functions + python_file.classes
        for class_ in python_file.classes:
            functions_and_classes += class_.methods
        functions_and_classes.sort(key=lambda x: x.start_line, reverse=True)
        code_lines = python_file.codestring.split("\n")
        for function_or_class in functions_and_classes:
            self.insert_llm_annotation(
                code_lines,
                function_or_class,
            )
        self.insert_llm_annotation(code_lines, python_file)
        return "\n".join(code_lines)

    def insert_llm_annotation(
        self,
        codelines: List[str],
        function_or_class_or_file: Union[CodeObject, PythonFile],
    ):
        response = function_or_class_or_file.llm_response
        if response == "":
            return

        start_line = (
            function_or_class_or_file.start_line
            if isinstance(function_or_class_or_file, (Function, Class))
            else 0
        )
        line_after_insert = codelines[start_line]
        indent = " " * (len(line_after_insert) - len(line_after_insert.lstrip()))
        to_add = [f"{indent}# {line}" for line in response.split("\n")]
        insert_elements(codelines, to_add, start_line)


class CopyRepositoryWithLLMDocstrings(CopyRepositoryWithLLMComments):
    """
    This class adds annotations to the code in form of docstrings.
    Old docstrings are preserved.
    """

    def insert_llm_annotation(
        self,
        codelines: List[str],
        function_or_class_or_file: Union[CodeObject, PythonFile],
    ):
        response = function_or_class_or_file.llm_response
        if response == "":
            return

        start_line = (
            function_or_class_or_file.docstring_line
            or function_or_class_or_file.start_line
            if isinstance(function_or_class_or_file, CodeObject)
            else 0
        )

        line_after_insert = codelines[start_line]
        indent = " " * (len(line_after_insert) - len(line_after_insert.lstrip()))

        docstring_start = f'{indent}"""'
        docstring_end = f'{indent}"""'

        line_after_insert = codelines[start_line]
        indent = " " * (len(line_after_insert) - len(line_after_insert.lstrip()))

        response = response.replace('"""', "").strip("\n")
        to_add = (
            [docstring_start]
            + [f"{indent}{line}" for line in response.split("\n")]
            + [docstring_end, ""]
        )
        insert_elements(codelines, to_add, start_line)
