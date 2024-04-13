from pathlib import Path

import pytest
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.clone_repository import clone_repository


@pytest.fixture(scope="session")
def config_optuna(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("test")
    config = BaseConfig(
        repository_name="optuna",
        repository_path=tmp_path / "optuna",
        remote_url="https://github.com/optuna/optuna.git",
        cache_path=tmp_path,
    )
    clone_repository(config)
    return config


@pytest.fixture(scope="session")
def config_llm_docstring_generator(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("test")
    config = BaseConfig(
        repository_name="llm_docstring_generator",
        repository_path=Path(__file__).parent.parent,
        cache_path=tmp_path,
    )
    return config
