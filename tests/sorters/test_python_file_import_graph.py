from llm_docstring_generator.parser.load_python_files import load_python_files
from llm_docstring_generator.sorters.sort_functions_and_classes import (
    get_sorted_functions_and_classes_and_methods,
)
from llm_docstring_generator.sorters.sort_python_files import (
    create_python_file_dependency_graph,
)
from tests.fixtures import config_optuna  # noqa: F401


def test_iterator_yields_correct_root_nodes(config_optuna):  # noqa: F811
    python_files = load_python_files(config_optuna)
    G = create_python_file_dependency_graph(python_files)
    root_nodes = [node for node, degree in G.in_degree() if degree == 0]

    for root_node in root_nodes:
        root_python_file = [
            python_file
            for python_file in python_files
            if python_file.import_name == root_node
        ][0]

        for function_or_class in get_sorted_functions_and_classes_and_methods(
            root_python_file
        ):
            if len(function_or_class.import_dependencies) == 0:
                continue
            elif set(
                [
                    import_dependency.import_name
                    for import_dependency in function_or_class.import_dependencies
                ]
            ) == {root_python_file.import_name}:
                continue
            else:
                raise AttributeError(
                    f"{function_or_class.import_}"
                    f" imports {function_or_class.import_dependencies}"
                )
