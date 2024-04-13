import ast
from typing import List

from llm_docstring_generator.parser.import_parser import extract_imports_from_codestring
from llm_docstring_generator.python_files.function_and_classes import Class, Function
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.sorters.get_import_dependencies import (
    extract_class_only_import_dependencies,
    extract_function_import_dependencies,
)
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.utils import (
    get_all_imports,
    remove_3rd_party_imports,
)


class DependencyResolver:
    """
    Class to resolve import dependencies within the codebase.
    Relies on function_import_graph logic to determine the overall file structure of the codebase.
    """

    def __init__(self, config: BaseConfig, codestring: str, import_name: str):
        self.config = config
        self.codestring = codestring
        self.import_name = import_name

    def extract_function_import_dependencies(
        self, import_: Import, function_node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> List[Import]:
        return extract_function_import_dependencies(
            self.config, import_, function_node=function_node
        )

    def extract_class_import_dependencies(
        self, import_: Import, methods: List[Function]
    ) -> List[Import]:
        class_import_dependencies = extract_class_only_import_dependencies(
            self.config, import_
        )
        method_import_dependencies = [
            item
            for sublist in [method.import_dependencies for method in methods]
            for item in sublist
        ]
        import_dependencies = list(
            set(class_import_dependencies + method_import_dependencies)
        )
        import_dependencies = sorted(
            import_dependencies, key=lambda x: x.complete_import_name
        )
        # exclude self-imports, i.e. methods that are defined in the same class
        return [
            import_dependency
            for import_dependency in import_dependencies
            if (
                import_dependency.import_name,
                import_dependency.class_or_function_name,
            )
            != (import_.import_name, import_.class_or_function_name)
        ]

    def extract_file_import_dependencies(
        self, functions: List[Function], classes: List[Class]
    ) -> List[Import]:
        """
        Extract all imports from a code string using ast parser and code2flow graph.
        :return: list of Import dataclasses
        """
        # all explicit imports the file has
        imports = extract_imports_from_codestring(
            codestring=self.codestring,
            import_name=self.import_name,
            all_imports=get_all_imports(self.config),
        )
        for function in functions:
            imports += function.import_dependencies
        for class_ in classes:
            imports += class_.import_dependencies
            for method in class_.methods:
                imports += method.import_dependencies

        # exclude imports that point to the same file, e.g. function foo calls function bar
        # from the same file
        imports = [
            import_ for import_ in imports if import_.import_name != self.import_name
        ]
        imports = list(set(imports))
        imports = remove_3rd_party_imports(self.config, imports)
        imports = sorted(imports, key=lambda x: x.complete_import_name)
        return imports
