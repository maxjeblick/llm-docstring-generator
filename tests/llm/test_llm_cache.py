import logging
import random

from faker import Faker
from llm_docstring_generator.annotator.code_annotator import DefaultFileAnnotator
from llm_docstring_generator.llm.cache_database import (
    CacheEntry,
    LLMCache,
    _create_scoped_session,
)
from llm_docstring_generator.llm.llm import BaseLLM, DebugLLM
from llm_docstring_generator.llm.llm_config import LLMConfig
from llm_docstring_generator.parser.load_python_files import load_python_files
from llm_docstring_generator.sorters.sort_python_files import (
    sort_python_files_by_imports,
)
from tests.fixtures import config_llm_docstring_generator  # noqa: F401

faker = Faker()


class RandomLLM(BaseLLM):
    def call_llm(self, prompt: str) -> str:
        return "".join([faker.sentence() for _ in range(random.randint(1, 15))])


class RaiseLLM(BaseLLM):
    def call_llm(self, prompt: str) -> str:
        raise Exception("This is a test exception")


def test_caching_integration_test(config_llm_docstring_generator):  # noqa: F811
    llm_cache = LLMCache(
        db_name="sqlite:///:memory:",
    )
    for llm_class in [RandomLLM, RaiseLLM]:
        llm = llm_class(config=LLMConfig(model="random"), llm_cache=llm_cache)
        python_files = load_python_files(config_llm_docstring_generator)
        python_files = sort_python_files_by_imports(python_files)

        annotator = DefaultFileAnnotator(llm=llm)
        annotator(python_files)


def test_caching(caplog):
    llm_cache = LLMCache(
        db_name="sqlite:///:memory:",
    )
    llm = DebugLLM(config=LLMConfig(), llm_cache=llm_cache)

    for prompt in [f"prompt{i}" for i in range(500)]:
        answer = llm(prompt)
        assert (
            llm_cache.get_llm_answer(
                prompt=prompt,
                prompt_truncated=prompt,
                system_prompt=llm.config.system_prompt,
                model=llm.config.model,
            )
            == answer
        )
        # assert logger.debug("Using cached result") is called
        with caplog.at_level(logging.DEBUG):
            llm(prompt)
        assert "Using cached result" in caplog.text, prompt
        caplog.clear()

    with _create_scoped_session(
        llm_cache.scoped_session, ignore_integrity_error=False
    ) as session:
        cache_entries = session.query(CacheEntry).all()
        assert len(cache_entries) == 500
