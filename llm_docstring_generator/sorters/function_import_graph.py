from functools import lru_cache
from pathlib import Path
from typing import List

import networkx as nx
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.sorters.code2flow_patched import code2flow_patched
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.utils import get_all_imports
from loguru import logger

__all__ = ["get_function_import_graph"]


@lru_cache(maxsize=None)
def get_function_import_graph(config: BaseConfig) -> nx.DiGraph:
    """
    Get the dependency graph for a repository.
    nodes are stored as Import objects, which contain the import name and the class or function name.
    """
    code2flow_save_path = config.cache_path / "out.gv"

    output_file = OutputFile()
    raw_source_paths = get_raw_source_paths(config)
    code2flow_patched(raw_source_paths, output_file)

    # using tempfile.NamedTemporaryFile caused failing tests, so we write the file to disk
    with open(code2flow_save_path, "w") as f:
        f.write(output_file.content)
    G = nx.nx_agraph.read_dot(code2flow_save_path)
    G = convert_code2flow_graph_to_import_graph(G, config)
    return G


def convert_code2flow_graph_to_import_graph(
    G: nx.DiGraph, config: BaseConfig
) -> nx.DiGraph:
    # Remove all nodes that don't have a name attribute; these are artifacts from the code2flow tool
    G.remove_nodes_from([node for node in G.nodes if G.nodes[node].get("name") is None])
    # Rename nodes to their import name. Current node's name attribute is a random hash
    mapping = {
        node: convert_code2flow_node_to_import_node(config.repository_path, G, node)
        for node in G.nodes
    }
    # rename label attribute. This is only needed for better visualization, as
    # .draw() uses the label attribute to name the nodes.
    # otherwise, the nodes would have ambiguous names such as __init__
    for node in G.nodes:
        G.nodes[node]["label"] = G.nodes[node]["name"].replace("::", ".")
    G = nx.relabel_nodes(G, mapping, copy=False)
    # remove all nodes that don't have class_or_function_name attribute; these are the actual files.
    G.remove_nodes_from(
        [
            node
            for node in G.nodes
            if not isinstance(node, Import) or node.class_or_function_name is None
        ]
    )
    logger.debug(
        f"Created code dependency Graph with {len(G.nodes)} nodes and {len(G.edges)} edges"
    )
    # add potential missing imports to the graph code2flow couldn't find
    # this makes G.successors(import_) work for all imports even if they are not resolved by code2flow
    all_imports = get_all_imports(config)
    G.add_nodes_from(all_imports)
    logger.debug(
        f"Added remaining nodes, graph now contains {len(G.nodes)} nodes and {len(G.edges)} edges"
    )
    return G


def convert_code2flow_node_to_import_node(
    repository_path: Path, G, node: str
) -> Import:
    # convert import name from stored information produced by code2flow
    root_dir = Path(G.nodes[node]["filename"]).relative_to(repository_path)
    class_or_function_name = G.nodes[node]["name"].split("::")[-1]
    method_name = None

    if "(global)" in class_or_function_name:
        class_or_function_name = None
    elif "." in class_or_function_name:
        class_or_function_name, method_name = class_or_function_name.split(".")[:2]

    return Import(
        import_name=str(root_dir).replace("/", ".")[:-3],
        class_or_function_name=class_or_function_name,
        method_name=method_name,
    )


class OutputFile:
    def __init__(self):
        self.content = ""

    def write(self, x: str):
        self.content = x


def get_raw_source_paths(config: BaseConfig) -> List[str]:
    if (config.repository_path / config.repository_name).exists():
        return [str(config.repository_path / config.repository_name)]
    else:
        # e.g. transformers library which uses transformers/src/transformers
        return [str(config.repository_path)]
