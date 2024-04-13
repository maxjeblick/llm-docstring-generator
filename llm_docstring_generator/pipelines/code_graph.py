import os
from pathlib import Path
from typing import List

import networkx as nx
from llm_docstring_generator.parser.load_python_files import load_python_files
from llm_docstring_generator.python_files.function_and_classes import Class, Function
from llm_docstring_generator.python_files.python_file import PythonFile
from llm_docstring_generator.sorters.sort_python_files import (
    create_python_file_dependency_graph,
)
from llm_docstring_generator.utils.base_config import DEFAULT_DATA_DIR, BaseConfig
from llm_docstring_generator.utils.clone_repository import clone_repository
from pyvis.network import Network


def run_code_graph_generation(
    repository_name: str,
    remote_url: str,
    data_dir: Path = DEFAULT_DATA_DIR,
    mode: str = "file_level",
    graph_filename: str = "out.html",
):
    """
    Generate a code graph for a given repository.
    Useful for debugging and understanding the codebase.
    """
    project_name = f"{repository_name}_project"
    config = BaseConfig(
        repository_name=repository_name,
        repository_path=data_dir / project_name / repository_name,
        remote_url=remote_url,
        cache_path=data_dir / project_name,
    )

    if not os.path.exists(config.repository_path):
        clone_repository(config)

    python_files = load_python_files(config)
    if mode == "file_level":
        G = create_python_file_dependency_graph(python_files)
    elif mode == "function_level":
        G = create_function_depencendy_graph(python_files)
    else:
        raise ValueError(f"mode {mode} not supported")

    nt = Network(
        height="750px",
        width="100%",
        bgcolor="#222222",
        font_color="white",
        select_menu=True,
    )
    nt.from_nx(G)
    nt.toggle_physics(True)
    nt.show_buttons()
    nt.show(graph_filename)


def create_function_depencendy_graph(python_files: List[PythonFile]):
    G = nx.DiGraph()
    all_functions_and_classes: List[Function | Class] = []
    for python_file in python_files:
        all_functions_and_classes.extend(python_file.functions)
        all_functions_and_classes.extend(python_file.classes)
        for class_ in python_file.classes:
            all_functions_and_classes.extend(class_.methods)
    G.add_nodes_from(
        [
            function_or_class.complete_import_name
            for function_or_class in all_functions_and_classes
        ]
    )
    for function_or_class in all_functions_and_classes:
        for import_ in function_or_class.import_dependencies:
            G.add_edge(
                function_or_class.complete_import_name, import_.complete_import_name
            )
    return G
