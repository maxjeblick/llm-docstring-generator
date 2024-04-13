"""
Series of tests that ensure that the sorting order of functions and classes is consistent across different runs.
In a previous version this was not the case, as the code uses list(set(...)) in various places, which can lead to
different ordering of the same list across different runs.

This caused issues with LLM annotations and caching.
As an example, if a function depends on 3 other functions, there are 6 potential orders in which the 3 functions
can be sorted. Thus, the metadata of the LLM annotation would be different across different runs, even though the
code is the same.
This caused caching to fail, and resulted in hard-to-debug issues.
"""

import hashlib
from pathlib import Path

import networkx as nx
from llm_docstring_generator.parser.load_python_files import (
    load_python_file,
    load_python_files,
)
from llm_docstring_generator.sorters.sort_functions_and_classes import (
    get_sorted_functions_and_classes_and_methods,
    get_sorted_import_names,
)
from llm_docstring_generator.sorters.sort_python_files import (
    sort_python_files_by_imports,
)
from tests.fixtures import config_llm_docstring_generator  # noqa: F401


def test_sorting_order_is_consistent(config_llm_docstring_generator):  # noqa: F811
    """
    TODO
        Test breaks and needs to be updated for any code change.
        Ideally, we would run the test multiple times using fresh python sessions and check if the order is consistent.
    """
    python_files = load_python_files(config_llm_docstring_generator)
    python_files = sort_python_files_by_imports(python_files)
    print([python_file.import_name for python_file in python_files])
    md5_python_file_hash = hashlib.md5(
        "".join([python_file.import_name for python_file in python_files]).encode()
    ).hexdigest()
    print(md5_python_file_hash)
    assert md5_python_file_hash == "d57f29207c62f2b61c09a8993c00d338"

    imports = []
    for python_file in python_files:
        imports.append(
            [
                function_or_class.import_.complete_import_name
                for function_or_class in get_sorted_functions_and_classes_and_methods(
                    python_file
                )
            ]
        )
    #
    md5_hashes = [
        hashlib.md5("".join(import_list).encode()).hexdigest()
        for import_list in imports
    ]
    print(md5_hashes)
    expected_hashes = [
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "9cacfdcd49fb160141605c8f0ff431c0",
        "ee0f610cab82b3a293af3bc669a05c5c",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "b75bbba2572620ea4b0ba4ab79a7e6ee",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "ccb5ae5c2759b9bd70fd4872bee7d1d8",
        "d41d8cd98f00b204e9800998ecf8427e",
        "4fd0b11d7e9a065c0da7496471f6882f",
        "d41d8cd98f00b204e9800998ecf8427e",
        "94a26e027692cf3f67866ebb5cba516e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "6966e621ba0fe3b0a17b86e1ddb719e0",
        "d41d8cd98f00b204e9800998ecf8427e",
        "c53f364553cbd11e5f0aff8e6ee68434",
        "bbaa110be593cfe88c90405a929c7e9c",
        "5e9411246cceef572a9f95de580ac74f",
        "2d58c9d4fe9683358de82732f9c7e569",
        "c2170fa26819ca44cb6119c1a7b2e789",
        "d9756b0b9edb67eadddf755a2c925cda",
        "3deb05c02502d02136ed02cc0adeb144",
        "734ef67ad2823f26abad7534ba9365c6",
        "5e6b2127a792b1b6caf8d7016b9dd0ea",
        "bfac517d98812b4349d8becc709af97f",
        "18a951d15288f1e829f0e3b6d90175d2",
        "307b661d0e25ef18ce063c57c0a7d25e",
        "46980c744e193108abbabec3340649c1",
        "0e51173d4858288bc881a02c478b4a52",
        "bd97ef3822ff31b6fdf5cde535b67aad",
        "fe93656f7f25a524977483215159b6f9",
        "c94c4b53547e7760187aa46fd425f92f",
        "02ad2b7f9a0c62ae67c01b676f2ae6c2",
        "ec9605b7a6a5706875a95a923c810d20",
        "572593139d634449e70aac902d34daa4",
        "3aae08b83a89e2e40aa4a6e0cb6bacaf",
        "d41d8cd98f00b204e9800998ecf8427e",
        "d41d8cd98f00b204e9800998ecf8427e",
        "9dc13da2c3f6b87e37770635eb9bfa27",
        "c0f4642534df2d33043c5da1a733f0bf",
        "7fb11c7d1018ac268ee8e01b80416914",
        "dc3974dc8c0ee9c3b0fe69906b7f6b5d",
        "be9e4a0292df289874f7fce5217f765a",
        "d247d3c27f129bc72f66ab4499e34153",
        "a8a53167ebfb9699cae5213ffd1f75a3",
        "c1517e5418f5cffab796a19fe20d9dda",
        "0cd7b3c798b631e2356dc4a504cfa6a2",
        "2853512e6935915e7d8fdfa535c0cba5",
        "eef2dc371b3f71333ac91eb731cb2005",
        "069a93657344fc995a7d2e164593140c",
        "367c8435bb127de082366f0b35ca3b9e",
        "22851deb3a2bca5a7e8af88b4c87f6f2",
        "c10551b502584201b859bf03a5e969ac",
        "c87f5882cf63ea48b76744a4408ed855",
        "8b1d3e661e5695c9c7d8a18027725e81",
    ]

    errors = []
    for python_file, md5_hash, expected_hash in zip(
        python_files, md5_hashes, expected_hashes
    ):
        if md5_hash != expected_hash:
            errors.append(python_file.import_name)

    assert not errors


def test_llm_is_sorted_correctly(config_llm_docstring_generator):  # noqa: F811
    python_file = load_python_file(
        config_llm_docstring_generator,
        Path(__file__).parent.parent.parent
        / "llm_docstring_generator"
        / "llm"
        / "llm.py",
    )

    function_and_classes = python_file.functions + python_file.classes
    for class_ in python_file.classes:
        function_and_classes += class_.methods
    function_and_classes = sorted(
        function_and_classes, key=lambda x: x.complete_import_name
    )
    assert ([f.import_.complete_import_name for f in function_and_classes]) == [
        "llm_docstring_generator.llm.llm.BaseLLM",
        "llm_docstring_generator.llm.llm.BaseLLM.__call__",
        "llm_docstring_generator.llm.llm.BaseLLM.__init__",
        "llm_docstring_generator.llm.llm.BaseLLM.call_llm",
        "llm_docstring_generator.llm.llm.BaseLLM.get_num_tokens",
        "llm_docstring_generator.llm.llm.BaseLLM.token_count_stats",
        "llm_docstring_generator.llm.llm.DebugLLM",
        "llm_docstring_generator.llm.llm.DebugLLM.call_llm",
        "llm_docstring_generator.llm.llm.LocalTGILLM",
        "llm_docstring_generator.llm.llm.LocalTGILLM.__init__",
        "llm_docstring_generator.llm.llm.LocalTGILLM.call_llm",
        "llm_docstring_generator.llm.llm.OpenAILLM",
        "llm_docstring_generator.llm.llm.OpenAILLM.__init__",
        "llm_docstring_generator.llm.llm.OpenAILLM.call_llm",
    ]

    import_names = get_sorted_import_names(python_file)
    expected = [
        "llm_docstring_generator.llm.cache_database.LLMCache.get_llm_answer",
        "llm_docstring_generator.llm.cache_database.LLMCache.save_llm_answer",
        "llm_docstring_generator.llm.cache_database.create_default_llm_cache",
        "llm_docstring_generator.llm.llm_config.LLMConfig",
        "llm_docstring_generator.llm.llm.BaseLLM.call_llm",
        "llm_docstring_generator.llm.llm.BaseLLM.get_num_tokens",
        "llm_docstring_generator.llm.llm.BaseLLM.token_count_stats",
        "llm_docstring_generator.llm.llm.DebugLLM",
        "llm_docstring_generator.llm.llm.DebugLLM.call_llm",
        "llm_docstring_generator.llm.llm.LocalTGILLM.call_llm",
        "llm_docstring_generator.llm.llm.OpenAILLM.call_llm",
        "llm_docstring_generator.llm.llm.BaseLLM",
        "llm_docstring_generator.llm.llm.BaseLLM.__init__",
        "llm_docstring_generator.llm.llm.LocalTGILLM",
        "llm_docstring_generator.llm.llm.LocalTGILLM.__init__",
        "llm_docstring_generator.llm.llm.OpenAILLM",
        "llm_docstring_generator.llm.llm.OpenAILLM.__init__",
        "llm_docstring_generator.llm.llm.BaseLLM.__call__",
    ]
    assert import_names == expected


def test_topological_sort_is_reproducible():
    """
    This tests confirms that nx.topological_sort is consistent across different runs.
    """
    import_dependencies_dict = {
        "llm_docstring_generator.llm.llm.BaseLLM": [
            "llm_docstring_generator.llm.cache_database.create_default_llm_cache",
            "llm_docstring_generator.llm.cache_database.LLMCache.save_llm_answer",
            "llm_docstring_generator.llm.cache_database.LLMCache.get_llm_answer",
            "llm_docstring_generator.configs.llm_config.LLMConfig",
        ],
        "llm_docstring_generator.llm.llm.BaseLLM.__call__": [
            "llm_docstring_generator.llm.llm.BaseLLM.get_num_tokens",
            "llm_docstring_generator.llm.cache_database.LLMCache.save_llm_answer",
            "llm_docstring_generator.llm.cache_database.LLMCache.get_llm_answer",
            "llm_docstring_generator.llm.llm.BaseLLM.call_llm",
        ],
        "llm_docstring_generator.llm.llm.BaseLLM.__init__": [
            "llm_docstring_generator.llm.cache_database.create_default_llm_cache",
            "llm_docstring_generator.configs.llm_config.LLMConfig",
        ],
        "llm_docstring_generator.llm.llm.BaseLLM.call_llm": [],
        "llm_docstring_generator.llm.llm.BaseLLM.get_num_tokens": [],
        "llm_docstring_generator.llm.llm.BaseLLM.token_count_stats": [],
        "llm_docstring_generator.llm.llm.DebugLLM": [],
        "llm_docstring_generator.llm.llm.DebugLLM.call_llm": [],
        "llm_docstring_generator.llm.llm.LocalTGILLM": [
            "llm_docstring_generator.configs.llm_config.LLMConfig"
        ],
        "llm_docstring_generator.llm.llm.LocalTGILLM.__init__": [
            "llm_docstring_generator.configs.llm_config.LLMConfig"
        ],
        "llm_docstring_generator.llm.llm.LocalTGILLM.call_llm": [],
        "llm_docstring_generator.llm.llm.OpenAILLM": [
            "llm_docstring_generator.configs.llm_config.LLMConfig"
        ],
        "llm_docstring_generator.llm.llm.OpenAILLM.__init__": [
            "llm_docstring_generator.configs.llm_config.LLMConfig"
        ],
        "llm_docstring_generator.llm.llm.OpenAILLM.call_llm": [],
    }

    G = nx.DiGraph()
    for function_or_class_complete_import_name in import_dependencies_dict:
        # add node, as import_dependencies may be an empty list and we need to ensure the node
        # is in the graph
        G.add_node(function_or_class_complete_import_name)
        for (
            import_dependency_complete_import_name
        ) in import_dependencies_dict[  # type:ignore
            function_or_class_complete_import_name
        ]:
            G.add_edge(
                import_dependency_complete_import_name,
                function_or_class_complete_import_name,
            )
    sorted_import_names = list(nx.topological_sort(G))
    expected = [
        "llm_docstring_generator.llm.cache_database.create_default_llm_cache",
        "llm_docstring_generator.llm.cache_database.LLMCache.save_llm_answer",
        "llm_docstring_generator.llm.cache_database.LLMCache.get_llm_answer",
        "llm_docstring_generator.configs.llm_config.LLMConfig",
        "llm_docstring_generator.llm.llm.BaseLLM.get_num_tokens",
        "llm_docstring_generator.llm.llm.BaseLLM.call_llm",
        "llm_docstring_generator.llm.llm.BaseLLM.token_count_stats",
        "llm_docstring_generator.llm.llm.DebugLLM",
        "llm_docstring_generator.llm.llm.DebugLLM.call_llm",
        "llm_docstring_generator.llm.llm.LocalTGILLM.call_llm",
        "llm_docstring_generator.llm.llm.OpenAILLM.call_llm",
        "llm_docstring_generator.llm.llm.BaseLLM",
        "llm_docstring_generator.llm.llm.BaseLLM.__init__",
        "llm_docstring_generator.llm.llm.LocalTGILLM",
        "llm_docstring_generator.llm.llm.LocalTGILLM.__init__",
        "llm_docstring_generator.llm.llm.OpenAILLM",
        "llm_docstring_generator.llm.llm.OpenAILLM.__init__",
        "llm_docstring_generator.llm.llm.BaseLLM.__call__",
    ]
    assert sorted_import_names == expected
