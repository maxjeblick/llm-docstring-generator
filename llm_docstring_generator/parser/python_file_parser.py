"""
Parse a .py file and extract classes, functions and imports from it.
"""
import ast
from typing import List, Optional

from llm_docstring_generator.parser.ast_parser import AstParser
from llm_docstring_generator.parser.dependency_resolver import DependencyResolver
from llm_docstring_generator.python_files.function_and_classes import Class, Function
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.utils.base_config import BaseConfig


class PythonFileParser:
    """
    Class to parse a code string and extract all functions and classes from it.
    """

    def __init__(self, config: BaseConfig, codestring: str, import_name: str):
        self.config = config
        self.codestring = codestring
        self.import_name = import_name

        self.ast_parser = AstParser(codestring=codestring)
        self.dependency_resolver = DependencyResolver(
            config=config, codestring=codestring, import_name=import_name
        )

    def extract_functions(self) -> List[Function]:
        """
        Extract all functions from a code string.
        """
        functions = [
            self.extract_function(function_node=function_node)
            for function_node in self.ast_parser.extract_function_nodes()
        ]
        return sorted(functions, key=lambda x: x.start_line)

    def extract_classes(self) -> List[Class]:
        """
        Extract all classes from a code string.
        """
        classes = [
            self.extract_class(node) for node in self.ast_parser.extract_class_nodes()
        ]
        return sorted(classes, key=lambda x: x.start_line)

    def extract_function(
        self,
        function_node: ast.FunctionDef | ast.AsyncFunctionDef,
        class_name: Optional[str] = None,
    ) -> Function:
        if class_name:
            import_ = Import(
                import_name=self.import_name,
                class_or_function_name=class_name,
                method_name=function_node.name,
            )
        else:
            import_ = Import(
                import_name=self.import_name,
                class_or_function_name=function_node.name,
            )

        import_dependencies = (
            self.dependency_resolver.extract_function_import_dependencies(
                import_=import_, function_node=function_node
            )
        )
        parsed_node_dict = self.ast_parser.parse_node(node=function_node)
        return Function(
            import_=import_,
            import_dependencies=import_dependencies,
            codestring=parsed_node_dict["codestring"],
            docstring=parsed_node_dict["docstring"],
            docstring_line=parsed_node_dict["docstring_line"],
            start_line=parsed_node_dict["start_line"],
            end_line=parsed_node_dict["end_line"],
        )

    def extract_class(self, class_node: ast.ClassDef) -> Class:
        import_ = Import(
            import_name=self.import_name,
            class_or_function_name=class_node.name,
        )
        methods = [
            self.extract_function(function_node=method_node, class_name=class_node.name)
            for method_node in self.ast_parser.extract_method_nodes_from_class_node(
                class_node=class_node
            )
        ]
        methods = sorted(methods, key=lambda x: x.start_line)
        import_dependencies = (
            self.dependency_resolver.extract_class_import_dependencies(
                import_=import_, methods=methods
            )
        )
        parsed_node_dict = self.ast_parser.parse_node(node=class_node)

        return Class(
            import_=import_,
            import_dependencies=import_dependencies,
            methods=methods,
            codestring=parsed_node_dict["codestring"],
            docstring=parsed_node_dict["docstring"],
            docstring_line=parsed_node_dict["docstring_line"],
            start_line=parsed_node_dict["start_line"],
            end_line=parsed_node_dict["end_line"],
        )

    def extract_file_import_dependencies(
        self, functions: List[Function], classes: List[Class]
    ) -> List[Import]:
        return self.dependency_resolver.extract_file_import_dependencies(
            functions=functions, classes=classes
        )
