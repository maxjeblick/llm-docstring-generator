import ast
import textwrap

from llm_docstring_generator.parser.import_parser import (
    ImportParser,
    extract_imports_from_codestring,
)
from llm_docstring_generator.python_files.imports import Import


def test_extract_imports_from_codestring():
    code = """
    import os
    from sys import path

    import filename1.function1
    from filename2 import function2

    import filename2.subfilename2 as alias_filename2
    from filename3.subfilename3 import function3 as alias_function3

    from . import dot_import_function
    """
    code = textwrap.dedent(code)

    all_imports = [
        Import(
            import_name="filename1",
            class_or_function_name="function1",
            method_name=None,
        ),
        Import(
            import_name="filename2",
            class_or_function_name="function2",
            method_name=None,
        ),
        Import(
            import_name="filename2.subfilename2",
            class_or_function_name=None,
            method_name=None,
        ),
        Import(
            import_name="filename3.subfilename3",
            class_or_function_name="function3",
            method_name=None,
        ),
    ]
    import_dependencies = extract_imports_from_codestring(
        codestring=code, import_name="test_import", all_imports=all_imports
    )
    assert len(import_dependencies) == 7
    assert set(import_dependencies) == {
        Import(import_name="os", class_or_function_name=None, method_name=None),
        Import(import_name="sys", class_or_function_name="path", method_name=None),
        Import(
            import_name="filename1",
            class_or_function_name="function1",
            method_name=None,
        ),
        Import(
            import_name="filename2",
            class_or_function_name="function2",
            method_name=None,
        ),
        Import(
            import_name="filename2.subfilename2",
            class_or_function_name=None,
            method_name=None,
        ),
        Import(
            import_name="filename3.subfilename3",
            class_or_function_name="function3",
            method_name=None,
        ),
        Import(
            import_name="test_import",
            class_or_function_name="dot_import_function",
            method_name=None,
        ),
    }


def test_get_imports_nodes():
    code = """
    import os
    from sys import path

    import filename1.function1
    from filename2 import function2

    import filename2.subfilename2 as alias_filename2, filename3.subfilename3 as alias_filename3
    from filename3.subfilename3 import function3 as alias_function3

    from . import dot_import_function
    """
    code = textwrap.dedent(code)
    import_parser = ImportParser(code, "my_function")
    import_from_nodes, import_nodes = import_parser.get_imports_names()
    assert len(import_from_nodes) == 4
    assert len(import_nodes) == 4  # splits up the import line with multiple imports

    for node in import_from_nodes:
        assert isinstance(node, ast.ImportFrom)
        assert len(node.names) == 1
    for node in import_nodes:
        assert isinstance(node, ast.Import)
        assert len(node.names) == 1
