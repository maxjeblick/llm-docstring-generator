from typing import List, Union

from llm_docstring_generator.python_files.function_and_classes import (
    Class,
    CodeObject,
    Function,
)
from llm_docstring_generator.python_files.python_file import PythonFile
from llm_docstring_generator.sorters.sort_functions_and_classes import (
    get_sorted_functions_and_classes_and_methods,
)
from loguru import logger


class BaseMetaDataProvider:
    def __init__(self, python_files: List[PythonFile]):
        self.python_files = python_files

    def get_function_metadata(self, function: Union[Function | Class]) -> str:
        raise NotImplementedError

    def get_class_metadata(self, class_: Class) -> str:
        raise NotImplementedError

    def get_python_file_metadata(self, python_file: PythonFile) -> str:
        raise NotImplementedError


class DefaultMetaDataProvider(BaseMetaDataProvider):
    def get_function_metadata(self, function: Union[Function | Class]) -> str:
        """
        Get metadata for a function
        :param function: Function to get metadata for
        :return: Metadata string
        """
        functions_and_classes_used = get_functions_and_classes_used(
            code_object=function, python_files=self.python_files
        )
        if len(functions_and_classes_used) == 0:
            return ""

        metainfo = f"{function.complete_import_name} uses the following {len(functions_and_classes_used)} functions:\n"
        for idx, function_imported in enumerate(functions_and_classes_used):
            llm_response = function_imported.llm_response
            if llm_response == "":
                logger.warning(
                    f"Function {function_imported.complete_import_name} that is used by {function.complete_import_name} "
                    f"has no annotation"
                )
            else:
                metainfo += (
                    f"Function {idx + 1}: Name {function_imported.complete_import_name}, "
                    f"annotation: {llm_response}\n"
                )
        return metainfo

    def get_class_metadata(self, class_: Class) -> str:
        return self.get_function_metadata(class_)

    def get_python_file_metadata(self, python_file: PythonFile) -> str:
        metainfo = f"Repository name: {python_file.repository_name}\n"
        parent_python_files = [
            pf
            for pf in self.python_files
            if pf.import_name in python_file.import_dependencies
        ]
        if len(parent_python_files) == 0:
            return metainfo

        metainfo += f"The file imports {len(parent_python_files)} dependencies:\n"
        for idx, parent_python_file in enumerate(parent_python_files):
            if parent_python_file.llm_response == "":
                logger.warning(
                    f"Python File {parent_python_file.import_name} "
                    f"that is imported by {python_file.import_name} has no annotation"
                )
            else:
                metainfo += (
                    f"Import {idx + 1}: Name {parent_python_file.import_name}, "
                    f"has the following overall functionality:"
                    f" {parent_python_file.llm_response}\n"
                )
        return metainfo


class ShortMetaDataProvider(BaseMetaDataProvider):
    def get_function_metadata(self, function: Union[Function | Class]) -> str:
        return (
            f"Function {function.import_} in file {function.complete_import_name} uses the following functions:"
            f" {[import_dependency.complete_import_name for import_dependency in function.import_dependencies]}"
        )

    def get_class_metadata(self, class_: Class) -> str:
        return (
            f"Class {class_.import_} in file {class_.complete_import_name}"
            f" uses the following classes: {[import_.complete_import_name for import_ in class_.import_dependencies]}"
        )

    def get_python_file_metadata(self, python_file: PythonFile) -> str:
        return f"Repository name: {python_file.repository_name}. Imports: {python_file.import_dependencies}"


class DebugMetaDataProvider(BaseMetaDataProvider):
    def get_function_metadata(self, function: Union[Function | Class]) -> str:
        functions_used = get_functions_and_classes_used(
            code_object=function, python_files=self.python_files
        )
        with_annotations = "\n".join(
            [str(f.import_) for f in functions_used if f.llm_response != ""]
        )
        without_annotations = "\n".join(
            [str(f.import_) for f in functions_used if f.llm_response == ""]
        )
        metainfo = f"Functions/Classes with annotations:\n{with_annotations}\n"
        metainfo += f"Functions/Classes without annotations:\n{without_annotations}\n"
        return metainfo

    def get_class_metadata(self, class_: Class) -> str:
        return self.get_function_metadata(class_)

    def get_python_file_metadata(self, python_file: PythonFile) -> str:
        parent_python_files = [
            pf
            for pf in self.python_files
            if pf.import_name
            in [import_.import_name for import_ in python_file.import_dependencies]
        ]
        metainfo = f"Parent python files with annotations: {[pf.import_name for pf in parent_python_files if pf.llm_response != '']}\n"
        metainfo += f"Parent python files without annotations: {[pf.import_name for pf in parent_python_files if pf.llm_response == '']}\n"
        return metainfo


class NoMetaDataProvider(BaseMetaDataProvider):
    def get_function_metadata(self, function: Union[Function | Class]) -> str:
        return ""

    def get_class_metadata(self, class_: Class) -> str:
        return ""

    def get_python_file_metadata(self, python_file: PythonFile) -> str:
        return ""


def get_functions_and_classes_used(
    code_object: CodeObject, python_files: List
) -> List[CodeObject]:
    """
    Get all functions used by code_object
    :param code_object: CodeObject to get functions used by
    :param python_files: List of all python files in the repository
    :return: List of functions/methods used by this class
    """
    all_code_objects = [
        function_or_class
        for python_file in python_files
        for function_or_class in get_sorted_functions_and_classes_and_methods(
            python_file
        )
    ]
    complete_import_dependencies = [
        import_dependency.complete_import_name
        for import_dependency in code_object.import_dependencies
    ]
    code_objects_used = [
        code_object
        for code_object in all_code_objects
        if code_object.complete_import_name in complete_import_dependencies
    ]
    return sorted(code_objects_used, key=lambda x: x.complete_import_name)
