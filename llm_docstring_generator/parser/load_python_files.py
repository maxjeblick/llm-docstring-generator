from pathlib import Path
from typing import List

from llm_docstring_generator.parser.python_file_parser import PythonFileParser
from llm_docstring_generator.python_files.python_file import PythonFile
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.utils import get_import_name
from loguru import logger


def load_python_files(config: BaseConfig) -> List[PythonFile]:
    assert config.repository_path.exists(), f"{config.repository_path} does not exist."
    python_files = [
        load_python_file(config=config, python_filepath=python_filepath)
        for python_filepath in config.repository_path.rglob("*.py")
    ]
    logger.info(f"Loaded {len(python_files)} python_files")
    return python_files


def load_python_file(config: BaseConfig, python_filepath: Path) -> PythonFile:
    with open(python_filepath, "r") as file:
        codestring = file.read()
    import_name = get_import_name(
        repository_path=config.repository_path, python_filepath=python_filepath
    )
    parser = PythonFileParser(
        config=config,
        codestring=codestring,
        import_name=import_name,
    )
    functions = parser.extract_functions()
    classes = parser.extract_classes()
    import_dependencies = parser.extract_file_import_dependencies(
        functions=functions, classes=classes
    )
    return PythonFile(
        repository_name=config.repository_name,
        import_name=import_name,
        codestring=codestring,
        functions=functions,
        classes=classes,
        import_dependencies=import_dependencies,
    )
