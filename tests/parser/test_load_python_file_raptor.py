import pytest
from llm_docstring_generator.parser.load_python_files import load_python_file
from llm_docstring_generator.python_files.imports import Import
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.clone_repository import clone_repository


@pytest.fixture(scope="module")
def config(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("data")
    config = BaseConfig(
        repository_name="raptor",
        repository_path=tmp_path / "raptor",
        remote_url="https://github.com/parthsarthi03/raptor.git",
        cache_path=tmp_path,
    )
    clone_repository(config=config)
    return config


def test_python_file_initializes_correctly(config):
    python_filepath = config.repository_path / "raptor/cluster_utils.py"
    python_file = load_python_file(config=config, python_filepath=python_filepath)

    assert "RANDOM_SEED = 224" in python_file.codestring
    assert python_file.import_name == "raptor.cluster_utils"
    assert python_file.repository_name == "raptor"
    assert set([c.import_ for c in python_file.classes]) == {
        Import(
            import_name="raptor.cluster_utils",
            class_or_function_name="ClusteringAlgorithm",
            method_name=None,
        ),
        Import(
            import_name="raptor.cluster_utils",
            class_or_function_name="RAPTOR_Clustering",
            method_name=None,
        ),
    }
    assert set([f.import_ for f in python_file.functions]) == {
        Import(
            import_name="raptor.cluster_utils",
            class_or_function_name="global_cluster_embeddings",
            method_name=None,
        ),
        Import(
            import_name="raptor.cluster_utils",
            class_or_function_name="local_cluster_embeddings",
            method_name=None,
        ),
        Import(
            import_name="raptor.cluster_utils",
            class_or_function_name="get_optimal_clusters",
            method_name=None,
        ),
        Import(
            import_name="raptor.cluster_utils",
            class_or_function_name="GMM_cluster",
            method_name=None,
        ),
        Import(
            import_name="raptor.cluster_utils",
            class_or_function_name="perform_clustering",
            method_name=None,
        ),
    }
    # TODO relative import .utils is not resolved
    assert set(python_file.import_dependencies) == set()
