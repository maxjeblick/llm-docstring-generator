from typing import List, Type

from llm_docstring_generator.annotator.metadata_provider import (
    BaseMetaDataProvider,
    DefaultMetaDataProvider,
)
from llm_docstring_generator.llm.llm import BaseLLM, DebugLLM
from llm_docstring_generator.python_files.function_and_classes import Class, Function
from llm_docstring_generator.python_files.python_file import PythonFile
from llm_docstring_generator.sorters.sort_functions_and_classes import (
    get_sorted_functions_and_classes_and_methods,
)
from loguru import logger
from tqdm import tqdm


class BaseAnnotator:
    def __init__(
        self,
        llm: BaseLLM,
        metadata_provider_class: Type[BaseMetaDataProvider] = DefaultMetaDataProvider,
    ):
        self.llm = llm
        self.metadata_provider_class = metadata_provider_class

    def __call__(self, python_files: List[PythonFile]) -> List[PythonFile]:
        metadata_provider = self.metadata_provider_class(python_files=python_files)
        iterator = tqdm(python_files)
        for python_file in iterator:
            iterator.set_description(
                f"Annotating {python_file.import_name}: {self.llm.token_count_stats}"
            )
            if python_file.codestring == "":
                logger.debug(
                    f"python_file {python_file.import_name} has no code string, not annotating."
                )
                continue
            # python_file annotation is an inplace mutations, so all python_files' annotations
            # that have been annotated so far are available for current python_file
            logger.debug(f"Annotating {python_file.import_name}")
            self.annotate_python_file(python_file, metadata_provider=metadata_provider)
        logger.info("Annotated all python files")
        # even though python_files are mutated in place, we return them to be able to use the
        # run method in a pipeline
        return python_files

    def annotate_python_file(
        self, python_file: PythonFile, metadata_provider: BaseMetaDataProvider
    ):
        for function_or_class in get_sorted_functions_and_classes_and_methods(
            python_file
        ):
            if isinstance(function_or_class, Function):
                metadata = metadata_provider.get_function_metadata(function_or_class)
                self.annotate_function(function_or_class, metadata)
            elif isinstance(function_or_class, Class):
                metadata = metadata_provider.get_class_metadata(function_or_class)
                self.annotate_class(function_or_class, metadata)
            else:
                raise ValueError(f"Unknown type {type(function_or_class)}")
        metadata = metadata_provider.get_python_file_metadata(python_file)
        self.annotate_complete_file(python_file, metadata)

    def annotate_function(self, function: Function, metadata: str) -> None:
        raise NotImplementedError

    def annotate_class(self, class_: Class, metadata: str) -> None:
        raise NotImplementedError

    def annotate_complete_file(self, python_file: PythonFile, metadata: str) -> None:
        raise NotImplementedError


class DefaultAnnotator(BaseAnnotator):
    def annotate_function(self, function: Function, metadata: str) -> None:
        code = "\n```python\n" + function.codestring + "\n```"
        prompt = f"{metadata}{code}"
        function.llm_response = self.llm(prompt=prompt)

    def annotate_class(self, class_: Class, metadata: str) -> None:
        code = "\n```python\n" + class_.codestring + "\n```"
        prompt = f"{metadata}{code}"
        class_.llm_response = self.llm(prompt=prompt)

    def annotate_complete_file(self, python_file: PythonFile, metadata: str) -> None:
        # do not annotate the whole file by default
        pass


class DefaultFileAnnotator(DefaultAnnotator):
    def annotate_complete_file(self, python_file: PythonFile, metadata: str) -> None:
        if len(python_file.codestring) < 1000:
            code = "\n```python\n" + python_file.codestring + "\n```"
            prompt = f"{metadata}{code}"
        else:
            prompt = (
                "The original code is too long, here is some important information:\n\n"
            )
            prompt += metadata
            if len(python_file.functions):
                prompt += "\n\nFunction annotations:\n"
                prompt += "\n".join(
                    [
                        f"{function_annotation.complete_import_name}:{function_annotation.llm_response}"
                        for function_annotation in python_file.functions
                    ]
                )
            if len(python_file.classes):
                prompt += "\n\nClass annotations:\n"
                prompt += "\n".join(
                    [
                        class_annotation.llm_response
                        for class_annotation in python_file.classes
                    ]
                )
        python_file.llm_response = self.llm(prompt)


class DebugAnnotator(BaseAnnotator):
    def __init__(
        self,
        llm: BaseLLM,
        metadata_provider_class: Type[BaseMetaDataProvider],
    ):
        super().__init__(llm, metadata_provider_class)
        assert isinstance(llm, DebugLLM), (
            "DebugAnnotator can only be used with DebugLLM model"
            " (otherwise can lead to inference costs)."
        )

    def annotate_function(self, function: Function, metadata: str) -> None:
        prompt = f"Import: {function.import_} \n Metadata: {metadata}"
        function.llm_response = self.llm(prompt=prompt)

    def annotate_class(self, class_: Class, metadata) -> None:
        prompt = f"Import name: {class_.import_} \n Metadata: {metadata}"
        class_.llm_response = self.llm(prompt=prompt)

    def annotate_complete_file(self, python_file: PythonFile, metadata) -> None:
        prompt = f"Import name: {python_file.import_name} \n Metadata: {metadata}"
        python_file.llm_response = self.llm(prompt=prompt)
