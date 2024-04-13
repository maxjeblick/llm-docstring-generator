import subprocess

from llm_docstring_generator.utils.base_config import BaseConfig
from loguru import logger


def clone_repository(config: BaseConfig):
    save_path = config.repository_path
    if save_path.exists():
        raise ValueError(f"{save_path} already exists")
    save_path.mkdir(parents=True, exist_ok=True)
    try:
        clone_command = f"git clone {config.remote_url} {save_path}"
        logger.info(f"Cloning {config.remote_url} to {save_path}")
        result = subprocess.run(
            clone_command,
            shell=True,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            error_message = result.stderr.decode()
            raise RuntimeError(
                f"Failed to clone {config.remote_url} to {save_path}. Error: {error_message}"
            )
        logger.info(f"Cloned {config.remote_url} to {save_path}")
    except Exception as e:
        save_path.rmdir()
        raise e
