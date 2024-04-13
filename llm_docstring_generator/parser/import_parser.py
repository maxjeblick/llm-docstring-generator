import ast
from copy import copy
from typing import List, Optional

from llm_docstring_generator.python_files.imports import Import


def extract_imports_from_codestring(
    codestring: str, import_name: str, all_imports: Optional[List[Import]] = None
) -> List[Import]:
    """
    Extract imports from codestring.
    The challenge is to map imports such as
    from foo.bar import baz to the correct Import object, e.g.
    Import(import_name='foo.bar', class_or_function_name='baz')
    (that is 'baz' is a function rather than a python file)
    """
    import_parser = ImportParser(
        codestring=codestring, import_name=import_name, all_imports=all_imports
    )
    return import_parser.extract_imports_from_codestring()


class ImportParser:
    def __init__(
        self,
        codestring: str,
        import_name: str,
        all_imports: Optional[List[Import]] = None,
    ):
        self.codestring = codestring
        self.import_name = import_name
        self.all_imports = all_imports or []

    def extract_imports_from_codestring(self) -> List[Import]:
        import_from_nodes, import_nodes = self.get_imports_names()
        imports = [
            self.extract_import_from_import_from_node(import_from_node)
            for import_from_node in import_from_nodes
        ]
        imports += [
            self.extract_import_from_import_node(import_node)
            for import_node in import_nodes
        ]
        return imports

    def get_imports_names(self) -> List:
        p = ast.parse(self.codestring)
        import_nodes = []
        for import_node in [
            node for node in ast.walk(p) if isinstance(node, ast.Import)
        ]:
            names = import_node.names
            for name in names:
                import_node.names = [name]
                import_nodes.append(copy(import_node))
        import_from_nodes = []
        for import_from_node in [
            node for node in ast.walk(p) if isinstance(node, ast.ImportFrom)
        ]:
            names = import_from_node.names
            for name in names:
                import_from_node.names = [name]
                import_from_nodes.append(copy(import_from_node))

        return [import_from_nodes, import_nodes]

    def extract_import_from_import_node(self, import_node: ast.Import):
        alias = import_node.names[0]
        potential_imports = [
            Import(import_name=alias.name),
            Import(import_name=self.import_name + "." + alias.name),
        ]
        if "." in alias.name:
            potential_imports.append(
                Import(
                    import_name=".".join(alias.name.split(".")[:-1]),
                    class_or_function_name=alias.name.split(".")[-1],
                ),
            )
        for potential_import in potential_imports:
            if potential_import in self.all_imports:
                return potential_import
        return potential_imports[0]

    def extract_import_from_import_from_node(self, import_from_node: ast.ImportFrom):
        # Read: "extract_import from import_from_node"
        alias = import_from_node.names[0]
        # if import is 'from . import Foo', node.module is None
        import_name = (
            import_from_node.module if import_from_node.module else self.import_name
        )
        name = alias.name
        potential_imports = [
            Import(import_name=import_name, class_or_function_name=name),
            Import(import_name=import_name + "." + name),
        ]
        for potential_import in potential_imports:
            if potential_import in self.all_imports:
                return potential_import
        return potential_imports[0]
