from typing import List

from llm_docstring_generator.annotator.code_annotator import BaseAnnotator
from llm_docstring_generator.parser.load_python_files import load_python_files
from llm_docstring_generator.python_files.python_file import PythonFile
from llm_docstring_generator.sorters.sort_python_files import (
    sort_python_files_by_imports,
)
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.clone_repository import clone_repository
from llm_docstring_generator.utils.copy_repository import CopyRepositoryBase
from loguru import logger


class CodeAnnotationPipeline:
    def __init__(
        self,
        config: BaseConfig,
        annotator: BaseAnnotator,
        copy_repository: CopyRepositoryBase,
        filter_python_files_function=lambda python_files: python_files,
        sort_python_files_function=sort_python_files_by_imports,
    ):
        self.config = config

        # you can modify the pipeline by adding or removing steps
        # for now, it is hardcoded until new use cases require it to be more flexible
        self.steps = [
            filter_python_files_function,
            sort_python_files_function,
            annotator,
            copy_repository,
        ]

    def run(self):
        if self.config.remote_url and self.config.repository_path.exists():
            logger.warning(
                f"{self.config.repository_path} already exists, skipping clone. "
                f"Please remove it if you want to clone again."
            )
        elif self.config.remote_url:
            clone_repository(self.config)
        python_files: List[PythonFile] = load_python_files(self.config)
        assert len(python_files) > 0, "No python files found in the repository"

        for step in self.steps:
            python_files = step(python_files=python_files)
        return python_files
