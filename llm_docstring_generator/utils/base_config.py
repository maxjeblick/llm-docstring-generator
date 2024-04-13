import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_DATA_DIR: Path = Path(
    os.getenv("LLM_DOCSTRING_GENERATOR_CACHE")
    or Path("~/.cache/llm_docstring_generator").expanduser()
).absolute()


@dataclass
class BaseConfig:
    """
    Dataclass to represent a repository.
    repository_name: Name of the repository, e.g. llm-docstring-generator
    repository_path: Path to the repository, e.g. ~/PycharmProjects/llm-docstring-generator
                     Leave empty if you want to clone the repository
    remote_url: Optional remote url of the repository, will be used to clone the repository
                if repository_path does not exist

    cache_path: Path where to store computation results.
                Defaults to ~/.cache/llm_docstring_generator/{repository_name}_project

    new_repository_path: New path where the annotated repository will be saved.
    """

    repository_name: str
    repository_path: Path = None  # type: ignore
    remote_url: Optional[str] = None
    cache_path: Path = None  # type: ignore
    new_repository_path: Path = None  # type: ignore

    def __post_init__(self):
        if self.repository_path is None and self.remote_url is None:
            raise ValueError(
                f"repository_path and remote_url cannot be both None for repository {self.repository_name}"
            )
        if self.cache_path is None:
            self.cache_path = DEFAULT_DATA_DIR / f"{self.repository_name}_project"
        self.cache_path = Path(self.cache_path).absolute()
        try:
            self.cache_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ValueError(
                f"Could not create cache directory {self.cache_path} for repository {self.repository_name}. "
                f"Make sure you have the right permissions."
            ) from e

        if self.repository_path is None:
            self.repository_path = self.cache_path / self.repository_name
        self.repository_path = Path(self.repository_path).absolute()

        if self.new_repository_path is None:
            self.new_repository_path = (
                self.cache_path / f"{self.repository_name}_annotated"
            )
        self.new_repository_path = Path(self.new_repository_path).absolute()

    def __hash__(self):
        # To be able tp use lru_cache with this class
        hash_str = (
            self.repository_name
            + str(self.repository_path)
            + str(self.remote_url)
            + str(self.new_repository_path)
        )
        return hash(hash_str)
