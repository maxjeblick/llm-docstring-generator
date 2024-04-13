import os
from pathlib import Path

import pytest
from llm_docstring_generator.utils.base_config import BaseConfig
from llm_docstring_generator.utils.clone_repository import clone_repository

SMALL_TEST_REPO_URL = "https://github.com/rtyley/small-test-repo.git"


def test_clone_repository_clones_repo(tmpdir):
    url = SMALL_TEST_REPO_URL
    save_path = Path(tmpdir) / "test_repo"
    config = BaseConfig(
        repository_path=save_path,
        repository_name="test_repo",
        cache_path=tmpdir,
        remote_url=url,
    )
    clone_repository(config=config)

    assert os.path.exists(save_path)
    assert os.path.exists(os.path.join(save_path, ".git"))


def test_clone_repository_fails_on_existing_repository(tmpdir):
    url = SMALL_TEST_REPO_URL
    save_path = Path(tmpdir) / "test_repo"
    config = BaseConfig(
        repository_path=save_path,
        repository_name="test_repo",
        cache_path=tmpdir,
        remote_url=url,
    )
    clone_repository(config=config)
    with pytest.raises(ValueError):
        clone_repository(config=config)
