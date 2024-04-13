from pathlib import Path

from llm_docstring_generator.parser.load_python_files import load_python_file
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.python_files.python_file import PythonFile
from tests.fixtures import config_llm_docstring_generator  # noqa: F401


def test_load_python_file_code_annotation_pipeline(
    config_llm_docstring_generator,  # noqa: F811
):
    python_filepath = (
        Path(__file__).parent.parent.parent
        / "llm_docstring_generator/pipelines/code_annotation_pipeline.py"
    )
    python_file: PythonFile = load_python_file(
        config_llm_docstring_generator, python_filepath
    )
    class_ = python_file.classes[0]
    assert (
        class_.import_.complete_import_name
        == "llm_docstring_generator.pipelines.code_annotation_pipeline.CodeAnnotationPipeline"
    )

    methods = class_.methods

    assert (
        methods[0].import_.complete_import_name
        == "llm_docstring_generator.pipelines.code_annotation_pipeline.CodeAnnotationPipeline.__init__"
    )
    assert (
        methods[1].import_.complete_import_name
        == "llm_docstring_generator.pipelines.code_annotation_pipeline.CodeAnnotationPipeline.run"
    )
    assert set(methods[0].import_dependencies) == {
        Import(
            import_name="llm_docstring_generator.annotator.code_annotator",
            class_or_function_name="BaseAnnotator",
            method_name=None,
        ),
        Import(
            import_name="llm_docstring_generator.utils.base_config",
            class_or_function_name="BaseConfig",
            method_name=None,
        ),
        Import(
            import_name="llm_docstring_generator.utils.copy_repository",
            class_or_function_name="CopyRepositoryBase",
            method_name=None,
        ),
    }

    assert set(methods[1].import_dependencies) == {
        Import(
            import_name="llm_docstring_generator.parser.load_python_files",
            class_or_function_name="load_python_files",
            method_name=None,
        ),
        Import(
            import_name="llm_docstring_generator.utils.clone_repository",
            class_or_function_name="clone_repository",
            method_name=None,
        ),
    }
