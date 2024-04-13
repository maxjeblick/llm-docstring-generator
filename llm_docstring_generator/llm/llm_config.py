from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from llm_docstring_generator.llm.prompts import DEFAULT_DOCSTRING_SYSTEM_PROMPT


@dataclass
class LLMConfig:
    system_prompt: str = DEFAULT_DOCSTRING_SYSTEM_PROMPT
    model: str = "gpt-3.5-turbo"
    db_root_path: Optional[Path] = None
    max_prompt_token_length: int = int(1e9)
