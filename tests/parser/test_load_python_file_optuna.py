from llm_docstring_generator.parser.load_python_files import load_python_file
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.sorters.sort_functions_and_classes import (
    get_sorted_functions_and_classes_and_methods,
)
from llm_docstring_generator.utils.base_config import BaseConfig
from tests.fixtures import config_optuna  # noqa: F401


def test_iterator_yields_correct_root_nodes(config_optuna: BaseConfig):  # noqa: F811
    file = config_optuna.repository_path / "optuna" / "_callbacks.py"
    python_file = load_python_file(config=config_optuna, python_filepath=file)
    """
    from typing import Any
    from typing import Container
    from typing import Dict
    from typing import List
    from typing import Optional
    import optuna
    from optuna._experimental import experimental_class
    from optuna._experimental import experimental_func
    from optuna.trial import FrozenTrial
    from optuna.trial import TrialState
    """
    # optuna._callbacks.py uses study.add_trial, which is not imported explicitly
    # optuna.trial.FrozenTrial and optuna.trial.TrialState
    # are alias to optuna.trial._frozen.FrozenTrial and optuna.trial._state.TrialState
    # They are not yet resolved correctly

    expected_imports = [
        Import(
            import_name="optuna.study.study",
            class_or_function_name="Study",
            method_name="stop",
        ),
        Import(
            import_name="optuna._experimental",
            class_or_function_name="experimental_func",
            method_name=None,
        ),
        Import(
            import_name="optuna._experimental",
            class_or_function_name="experimental_class",
            method_name=None,
        ),
        Import(
            import_name="optuna.study.study",
            class_or_function_name="Study",
            method_name="add_trial",
        ),
    ]
    assert set(python_file.import_dependencies) == set(expected_imports)

    for function_or_class in get_sorted_functions_and_classes_and_methods(python_file):
        if function_or_class.import_ == Import(
            import_name="optuna._callbacks",
            class_or_function_name="RetryFailedTrialCallback",
            method_name="__call__",
        ):
            assert function_or_class.import_dependencies == [
                Import(
                    import_name="optuna.study.study",
                    class_or_function_name="Study",
                    method_name="add_trial",
                )
            ]
            break
    else:
        assert False, "Could not find the function_or_class with the import_"


# Recursion: _compute_rec calls _compute_exclusive_hv which then calls _compute_rec
EXCLUDE = ["optuna._hypervolume.wfg"]


def test_import_sorted_correctly(config_optuna):  # noqa: F811
    # wfg.py does not import code from other optuna modules, so can test in isolation
    python_file = load_python_file(
        config=config_optuna,
        python_filepath=config_optuna.repository_path
        / "optuna"
        / "_hypervolume"
        / "wfg.py",
    )
    function_imports_visited = []
    for function_or_class in get_sorted_functions_and_classes_and_methods(python_file):
        function_imports_visited.append(function_or_class.import_)
        if function_or_class.import_.import_name in EXCLUDE:
            continue

        for import_dependency in function_or_class.import_dependencies:
            if import_dependency not in function_imports_visited:
                raise AssertionError(
                    f"{function_or_class.import_} depends on {import_dependency}. That was not visited"
                )
