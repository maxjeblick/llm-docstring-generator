from llm_docstring_generator.annotator.metadata_provider import (
    get_functions_and_classes_used,
)
from llm_docstring_generator.parser.load_python_files import load_python_files
from llm_docstring_generator.sorters.sort_functions_and_classes import (
    get_sorted_functions_and_classes_and_methods,
)
from llm_docstring_generator.sorters.sort_python_files import (
    sort_python_files_by_imports,
)
from tests.fixtures import config_llm_docstring_generator  # noqa: F401


def test_python_file_sorter_does_not_remove_files(
    config_llm_docstring_generator,  # noqa: F811
):
    python_files = load_python_files(config_llm_docstring_generator)

    python_files_sorted = sort_python_files_by_imports(python_files=python_files)

    assert len(python_files) == len(python_files_sorted) > 25, (
        len(python_files),
        len(python_files_sorted),
        [python_file.import_name for python_file in python_files_sorted],
    )


def test_python_file_sorter_sorts_correctly(
    config_llm_docstring_generator,  # noqa: F811
):
    python_files = load_python_files(config_llm_docstring_generator)

    python_files_sorted = sort_python_files_by_imports(python_files=python_files)
    num_used = 0
    for python_file in python_files_sorted:
        python_file.llm_response = "annotated"
        for function_or_class in get_sorted_functions_and_classes_and_methods(
            python_file
        ):
            function_or_class.llm_response = "annotated"
            used_codeobjects = get_functions_and_classes_used(
                function_or_class, python_files
            )
            num_used += len(used_codeobjects)
            for used_codeobject in used_codeobjects:
                assert used_codeobject.llm_response == "annotated"

    assert num_used > 65, num_used


def test_iterator_resolves_imports_correctly(
    config_llm_docstring_generator,  # noqa: F811
):
    python_files = load_python_files(config_llm_docstring_generator)
    function_imports_visited = set()
    sorted_python_files = sort_python_files_by_imports(python_files=python_files)
    for idx, python_file in enumerate(sorted_python_files):
        for function_or_class in get_sorted_functions_and_classes_and_methods(
            python_file
        ):
            function_imports_visited.add(function_or_class.import_)

            for import_dependency in function_or_class.import_dependencies:
                if import_dependency not in function_imports_visited:
                    x = [
                        f.import_
                        for f in get_sorted_functions_and_classes_and_methods(
                            python_file
                        )
                    ]
                    raise AssertionError(
                        f"{function_or_class.import_} depends on {import_dependency}. That was not visited. {x}"
                    )

    assert idx == len(python_files) - 1
