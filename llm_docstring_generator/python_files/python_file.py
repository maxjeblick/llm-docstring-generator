from dataclasses import dataclass
from typing import List

from llm_docstring_generator.python_files.function_and_classes import Class, Function
from llm_docstring_generator.python_files.imports import Import


@dataclass
class PythonFile:
    """
    A class to represent a python file
    """

    repository_name: str  # The name of the repository
    import_name: str  # The name of the file to import, e.g. 'os.path'
    codestring: str  # The code string of the file
    functions: List[Function]  # The functions in the file
    classes: List[Class]  # The classes in the file
    # The import dependencies in the file. Also takes into account implicit dependencies, e.g. if a function
    # argument is a class from another file, this class will be added to the import_dependencies (via code2flow)
    import_dependencies: List[Import]
    # LLM annotation response from the LLM
    llm_response: str = ""
