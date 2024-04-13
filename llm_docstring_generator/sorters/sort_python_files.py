from itertools import cycle
from typing import List

import networkx as nx
from llm_docstring_generator.python_files.python_file import PythonFile
from loguru import logger


def sort_python_files_by_imports(python_files: List[PythonFile]) -> List[PythonFile]:
    """
    Sorts the python_files in a topological order based on the dependency graph.
    """
    name2python_file = {
        python_file.import_name: python_file for python_file in python_files
    }
    python_files_sorted = [
        name2python_file[import_name]
        for import_name in NodeIterator(
            G=create_python_file_dependency_graph(python_files)
        )
    ]

    logger.debug(f"Sorted {len(python_files)} python_files as follows:")
    logger.debug([pf.import_name for pf in python_files])
    return python_files_sorted


class NodeIterator:
    def __init__(self, G: nx.DiGraph):
        self.G = G
        self.nodes: List[str] = list(self.G.nodes)
        self.root_nodes: List[str] = sorted(
            [node for node, degree in self.G.in_degree() if degree == 0]
        )
        self.visited: List[str] = []
        self.loop_count = 0

    @property
    def not_visited(self):
        return sorted(list(set(self.nodes) - set(self.visited)))

    def __iter__(self):
        """
        Iterate over the nodes of the graph. The nodes are visited in a topological order.
        When a node is returned, all its predecessors (it's imports) have already been visited.
        :return:
        """
        yield from self.root_nodes
        self.visited = self.root_nodes

        parent_nodes_cycle = cycle(self.not_visited)
        while self.not_visited:
            node: str = next(parent_nodes_cycle)
            # factor 4 is arbitrary, but should be large enough to ensure that all nodes are visited
            should_break = self.loop_count > len(self.nodes) * 4
            if self.should_visit_node(node) or should_break:
                if should_break:
                    logger.warning(
                        f"Stopping condition reached. {node} depends on "
                        f"the following imports {[n for n in self.G.predecessors(node) if n not in self.visited]} "
                        f"that have not yet been visited."
                    )
                yield node

                self.visited.append(node)
                parent_nodes_cycle = cycle(self.not_visited)
                self.loop_count = 0
            else:
                self.loop_count += 1

    def should_visit_node(self, node):
        parent_nodes_visited = all(
            [parent_node in self.visited for parent_node in self.G.predecessors(node)]
        )
        return parent_nodes_visited and node not in self.visited


def create_python_file_dependency_graph(python_files: List[PythonFile]) -> nx.DiGraph:
    """
    Get the dependency graph for a repository.
    This is on a file-level basis, i.e. nodes are e.g. os.path
    nodes are stored as import strings, e.g.
    node = "llm_docstring_generator.python_dataclasses"
    """
    all_import_names: List[str] = [
        python_file.import_name for python_file in python_files
    ]

    G = nx.DiGraph()
    # add all nodes to ensure that files that are not imported are still in the graph
    G.add_nodes_from(all_import_names)

    for python_file in python_files:
        import_name: str = python_file.import_name
        for import_dependency in python_file.import_dependencies:
            import_dependency_filename = import_dependency.import_name
            # remove imports such as "import os"
            if import_dependency_filename in all_import_names:
                G.add_edge(import_dependency_filename, import_name)
    return G
