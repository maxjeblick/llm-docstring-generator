from llm_docstring_generator.parser.load_python_files import load_python_files
from llm_docstring_generator.utils.utils import get_all_imports
from tests.fixtures import config_llm_docstring_generator  # noqa: F401


def test_python_file_sorter_sorts_correctly(
    config_llm_docstring_generator,  # noqa: F811
):
    all_code_imports = get_all_imports(config_llm_docstring_generator)

    all_code_imports_2 = []
    python_files = load_python_files(config_llm_docstring_generator)
    for python_file in python_files:
        for function in python_file.functions:
            all_code_imports_2 += [function.import_]
        for class_ in python_file.classes:
            all_code_imports_2 += [class_.import_]
            for method in class_.methods:
                all_code_imports_2 += [method.import_]

    assert set(all_code_imports) == set(all_code_imports_2), (
        set(all_code_imports) - set(all_code_imports_2),
        set(all_code_imports_2) - set(all_code_imports),
    )
