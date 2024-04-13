from typing import Dict, List

import networkx as nx
from llm_docstring_generator.python_files.function_and_classes import Class, Function
from llm_docstring_generator.python_files.python_file import PythonFile
from loguru import logger


def get_sorted_functions_and_classes_and_methods(
    python_file: PythonFile,
) -> List[Function | Class]:
    """
    Sort functions and classes according to their relative dependencies, e.g. if function A
    calls function B, then B will be sorted after A (and B can thus have access to A's llm annotation).
    """
    sorted_import_names = get_sorted_import_names(python_file)

    function_and_classes = python_file.functions + python_file.classes
    for class_ in python_file.classes:
        function_and_classes += class_.methods

    return sorted(
        function_and_classes,
        key=lambda x: sorted_import_names.index(x.complete_import_name),
    )


# cannot use lru cache with python_file as argument
SORTED_IMPORT_NAMES_CACHE: Dict[str, List[str]] = dict()


def get_sorted_import_names(python_file: PythonFile) -> List[str]:
    if python_file.import_name in SORTED_IMPORT_NAMES_CACHE:
        return SORTED_IMPORT_NAMES_CACHE[python_file.import_name]

    function_and_classes = python_file.functions + python_file.classes
    for class_ in python_file.classes:
        function_and_classes += class_.methods
    function_and_classes = sorted(
        function_and_classes, key=lambda x: x.complete_import_name
    )
    try:
        G = nx.DiGraph()
        for function_or_class in function_and_classes:
            # add node, as import_dependencies may be an empty list and we need to ensure the node
            # is in the graph
            G.add_node(function_or_class.complete_import_name)
            for import_dependency in function_or_class.import_dependencies:
                G.add_edge(
                    import_dependency.complete_import_name,
                    function_or_class.complete_import_name,
                )
        sorted_import_names: List[str] = list(nx.topological_sort(G))

    except nx.NetworkXUnfeasible:
        logger.warning(
            f"Cyclic imports detected for {python_file.import_name}, sorting by start line"
        )
        sorted_import_names = [
            function_or_class.complete_import_name
            for function_or_class in sorted(
                function_and_classes, key=lambda x: x.start_line
            )
        ]
    SORTED_IMPORT_NAMES_CACHE[python_file.import_name] = sorted_import_names
    return sorted_import_names
