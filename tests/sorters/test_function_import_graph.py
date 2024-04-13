from pathlib import Path

from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.sorters.function_import_graph import (
    get_function_import_graph,
    get_raw_source_paths,
)
from llm_docstring_generator.utils.base_config import BaseConfig


def test_get_function_import_graph(tmp_path):
    config = BaseConfig(
        repository_name="mock_repo",
        repository_path=Path(__file__).parent / "mock_repo",
        cache_path=tmp_path,
    )
    G = get_function_import_graph(config=config)

    expected_nodes = [
        Import(
            import_name="a",
            class_or_function_name="DummyClass",
            method_name="__eq__",
        ),
        Import(
            import_name="a",
            class_or_function_name="DummyClass",
            method_name="__init__",
        ),
        Import(
            import_name="a",
            class_or_function_name="DummyClass",
            method_name="__repr__",
        ),
        Import(
            import_name="a",
            class_or_function_name="DummyDataclass",
            method_name="__eq__",
        ),
        Import(
            import_name="a",
            class_or_function_name="DummyDataclass",
            method_name="__repr__",
        ),
        Import(
            import_name="a",
            class_or_function_name="create_dummy_classes",
            method_name=None,
        ),
        Import(
            import_name="b",
            class_or_function_name="dummy_process",
            method_name=None,
        ),
        Import(import_name="c", class_or_function_name="dummy_a", method_name=None),
        Import(import_name="c", class_or_function_name="dummy_b", method_name=None),
        Import(import_name="b", class_or_function_name="inner", method_name=None),
        Import(
            import_name="a", class_or_function_name="DummyDataclass", method_name=None
        ),
        Import(import_name="a", class_or_function_name="DummyClass", method_name=None),
    ]

    assert set(list(G.nodes)) == set(expected_nodes)

    expected_edges = {
        (
            Import(
                import_name="a",
                class_or_function_name="create_dummy_classes",
                method_name=None,
            ),
            Import(
                import_name="a",
                class_or_function_name="DummyClass",
                method_name="__init__",
            ),
        ),
        (
            Import(import_name="c", class_or_function_name="dummy_a", method_name=None),
            Import(
                import_name="b",
                class_or_function_name="dummy_process",
                method_name=None,
            ),
        ),
        (
            Import(import_name="c", class_or_function_name="dummy_a", method_name=None),
            Import(import_name="c", class_or_function_name="dummy_b", method_name=None),
        ),
        (
            Import(import_name="c", class_or_function_name="dummy_b", method_name=None),
            Import(
                import_name="b",
                class_or_function_name="dummy_process",
                method_name=None,
            ),
        ),
        (
            Import(import_name="c", class_or_function_name="dummy_b", method_name=None),
            Import(import_name="c", class_or_function_name="dummy_a", method_name=None),
        ),
    }

    assert set(list(G.edges())) == expected_edges


def test_get_function_import_graph_2():
    raw_source_paths = get_raw_source_paths(
        BaseConfig(
            repository_path=Path(__file__).parent / "mock_repo",
            repository_name="mock_repo",
        )
    )
    assert raw_source_paths == [str(Path(__file__).parent / "mock_repo")]
