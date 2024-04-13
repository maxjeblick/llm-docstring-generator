import os
from functools import lru_cache
from pathlib import Path
from typing import List

from llm_docstring_generator.parser.ast_parser import AstParser
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.utils.base_config import BaseConfig


def get_import_name(repository_path: Path, python_filepath: Path) -> str:
    """
    Get the import name of a python file. The import name is the relative path of the file w.r.t the repository
    e.g. llm_docstring_generator.python_file, if the file
    location is llm_docstring_generator/python_files/python_file.py
    """
    relative_filepath = python_filepath.relative_to(repository_path)
    import_name_with_ending = ".".join(relative_filepath.parts)
    import_name, ext = os.path.splitext(import_name_with_ending)
    if ext == ".py":
        return import_name
    else:
        raise ValueError(f"File {python_filepath} is not a python file")


@lru_cache(maxsize=None)
def get_all_imports(config: BaseConfig) -> list[Import]:
    imports = []

    for python_filepath in config.repository_path.rglob("*.py"):
        with open(python_filepath, "r") as file:
            codestring = file.read()
        import_name = get_import_name(
            repository_path=config.repository_path, python_filepath=python_filepath
        )
        parser = AstParser(codestring=codestring)
        function_nodes = parser.extract_function_nodes()
        imports += [
            Import(
                import_name=import_name,
                class_or_function_name=function_node.name,
                method_name=None,
            )
            for function_node in function_nodes
        ]

        class_nodes = parser.extract_class_nodes()
        imports += [
            Import(
                import_name=import_name,
                class_or_function_name=class_node.name,
                method_name=None,
            )
            for class_node in class_nodes
        ]
        for class_node in class_nodes:
            method_nodes = parser.extract_method_nodes_from_class_node(class_node)
            imports += [
                Import(
                    import_name=import_name,
                    class_or_function_name=class_node.name,
                    method_name=method_node.name,
                )
                for method_node in method_nodes
            ]
    return imports


def remove_3rd_party_imports(config: BaseConfig, imports: List[Import]):
    """
    Remove imports from 3d party libraries

    Note that this may also remove redirected imports,
    e.g.
        from optuna.trial import FrozenTrial
    is actually
        from optuna.trial._frozen import FrozenTrial
    but it is redefined in __init__.py
    all_imports will only contain Import("optuna.trial._frozen", "FrozenTrial", None)
    so Import("optuna.trial", "FrozenTrial", None) would be removed here.
    """
    all_imports = get_all_imports(config)
    return [import_ for import_ in imports if import_ in all_imports]
