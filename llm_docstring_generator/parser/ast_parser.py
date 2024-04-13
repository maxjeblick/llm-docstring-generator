import ast
import textwrap
from typing import List, Optional


class AstParser:
    def __init__(self, codestring: str):
        self.codestring = codestring

    def extract_function_nodes(self) -> List[ast.FunctionDef | ast.AsyncFunctionDef]:
        """
        Extract all functions from a code string.
        """
        p = ast.parse(self.codestring)
        nodes = list(ast.walk(p))
        # mark methods to be able to exclude them from the list of functions
        for node in nodes:
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        child.parent = node  # type: ignore
        function_nodes = [
            node
            for node in nodes
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not hasattr(node, "parent")
        ]
        return function_nodes

    def extract_class_nodes(self) -> List[ast.ClassDef]:
        """
        Extract all classes from a code string.
        """
        p = ast.parse(self.codestring)
        class_nodes = [node for node in ast.walk(p) if isinstance(node, ast.ClassDef)]
        return class_nodes

    def extract_method_nodes_from_class_node(
        self, class_node: ast.ClassDef
    ) -> List[ast.FunctionDef | ast.AsyncFunctionDef]:
        method_nodes = [
            node
            for node in ast.walk(class_node)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]
        return method_nodes

    def get_docstring_line(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef
    ) -> Optional[int]:
        # adapted from https://github.com/MichaelisTrofficus/gpt4docstrings
        docstring_line = None
        if (
            hasattr(node, "body")
            and len(node.body) > 0
            and hasattr(node.body[0], "lineno")
        ):
            docstring_line = node.body[0].lineno - 1
        return docstring_line

    def parse_node(
        self, node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
    ) -> dict:
        return dict(
            # cannot use astunparse here, as it automatically reformats the code
            # dedent the code string to remove leading whitespaces
            codestring=textwrap.dedent(
                "\n".join(
                    self.codestring.split("\n")[node.lineno - 1 : node.end_lineno]
                )
            ),
            docstring=ast.get_docstring(node),
            docstring_line=self.get_docstring_line(node),
            # lineno is 1-indexed, here codelines[start_line:end_line] gives the function without the decorators
            # or any newlines
            start_line=node.lineno - 1,
            end_line=node.end_lineno,
        )
