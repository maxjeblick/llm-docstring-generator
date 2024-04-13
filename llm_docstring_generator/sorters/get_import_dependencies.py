import ast
from functools import lru_cache
from typing import List

from llm_docstring_generator.parser.import_parser import extract_imports_from_codestring
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.sorters.function_import_graph import (
    get_function_import_graph,
)
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.utils import (
    get_all_imports,
    remove_3rd_party_imports,
)
from loguru import logger

__all__ = [
    "extract_function_import_dependencies",
    "extract_class_only_import_dependencies",
]


def extract_class_only_import_dependencies(
    config: BaseConfig, import_: Import
) -> List[Import]:
    return get_code2flow_import_dependencies(config, import_)


@lru_cache(maxsize=None)
def extract_function_import_dependencies(
    config: BaseConfig,
    import_: Import,
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> List[Import]:
    import_dependencies = get_code2flow_import_dependencies(config, import_)

    # this should be in responsibility of code2flow, but need to be done here for nowt
    try:
        import_dependencies_from_type_annotations = (
            extract_import_dependendencies_from_type_annotations(
                config=config,
                import_name=import_.import_name,
                function_node=function_node,
            )
        )
        import_dependencies += import_dependencies_from_type_annotations
        import_dependencies = list(set(import_dependencies))
        import_dependencies = sorted(
            import_dependencies, key=lambda x: x.complete_import_name
        )
    except Exception as e:
        logger.warning(
            f"Could not find type annotation imports for {import_.complete_import_name} due to {e}"
        )
    return import_dependencies


@lru_cache(maxsize=None)
def get_code2flow_import_dependencies(
    config: BaseConfig, import_: Import
) -> List[Import]:
    """
    Get all import_dependencies for a given import_.
    """
    try:
        G = get_function_import_graph(config)
        import_dependencies: List[Import] = list(G.successors(import_))

        if import_ in import_dependencies:
            logger.warning(
                f"Found a cyclic self-reference for {import_.complete_import_name}, deleting"
            )
            import_dependencies = list(set(import_dependencies) - {import_})
            import_dependencies = sorted(
                import_dependencies, key=lambda x: x.complete_import_name
            )
        logger.debug(
            f"Found {len(import_dependencies)} imports for {import_.complete_import_name}"
        )
    except Exception as e:
        logger.warning(
            f"Could not find imports for {import_.complete_import_name} due to {e}"
        )
        import_dependencies = []
    return import_dependencies


def extract_import_dependendencies_from_type_annotations(
    config: BaseConfig,
    import_name: str,
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> List[Import]:
    """
    Try to extract import dependencies from type annotations.

    This is useful to detect dependencies. e.g. if
        def eval(model: MyModel):
            ...
    then we can infer that MyModel is a dependency of eval.
    """
    # this fails if the python name contains . e.g.
    # optuna/optuna/storages/_rdb/alembic/versions/v1.2.0.a.py
    # As this isn't common, there is no try to fix this atm
    with open(
        config.repository_path / (import_name.replace(".", "/") + ".py"), "r"
    ) as file:
        codestring = file.read()

    file_imports = extract_imports_from_codestring(
        codestring=codestring,
        import_name=import_name,
        all_imports=get_all_imports(config),
    )
    file_imports = remove_3rd_party_imports(config, file_imports)

    import_annotations: List[Import] = []
    for type_annotation in parse_type_annotations(function_node):
        for import_ in file_imports:
            if type_annotation is not None and type_annotation in [
                import_.class_or_function_name,
                import_.method_name,
            ]:
                import_annotations.append(import_)
                break
    return import_annotations


def parse_type_annotations(
    function_node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> List[str]:
    if not function_node.args:
        return []

    return [
        ast.unparse(arg.annotation)
        for arg in function_node.args.args
        if arg.annotation is not None
    ]
