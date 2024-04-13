import os
from typing import Optional

import tiktoken
from huggingface_hub import InferenceClient
from llm_docstring_generator.llm.cache_database import (
    LLMCache,
    create_default_llm_cache,
)
from llm_docstring_generator.llm.llm_config import LLMConfig
from loguru import logger
from openai import OpenAI


class BaseLLM:
    """
    Base class for a language model.
    Uses a cache database to store the results of the llm calls.
    """

    def __init__(self, config: LLMConfig, llm_cache=None):
        self.config = config
        self.num_prompt_tokens = 0
        self.num_answer_tokens = 0

        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.llm_cache: Optional[LLMCache] = llm_cache or create_default_llm_cache(
            config
        )

    @property
    def token_count_stats(self) -> str:
        return f"(Approx.) total tokens used: Prompt tokens: {self.num_prompt_tokens}, Answer tokens: {self.num_answer_tokens}"

    def __call__(self, prompt: str) -> str:
        prompt_truncated = self.encoder.decode(
            self.encoder.encode(prompt, allowed_special="all")[
                : self.config.max_prompt_token_length
            ]
        )
        self.num_prompt_tokens += self.get_num_tokens(prompt_truncated, is_prompt=True)
        if self.llm_cache is None:
            answer = self.call_llm(prompt_truncated)
        else:
            cache_entry = self.llm_cache.get_llm_answer(
                prompt=prompt,
                prompt_truncated=prompt_truncated,
                system_prompt=self.config.system_prompt,
                model=self.config.model,
            )
            if cache_entry:
                logger.debug("Using cached result")
                answer = cache_entry
            else:
                answer = self.call_llm(prompt_truncated)
                self.llm_cache.save_llm_answer(
                    prompt=prompt,
                    prompt_truncated=prompt_truncated,
                    answer=answer,
                    system_prompt=self.config.system_prompt,
                    model=self.config.model,
                )
        self.num_answer_tokens += self.get_num_tokens(answer, is_prompt=False)
        return answer

    def get_num_tokens(self, text: str, is_prompt: bool):
        """
        Get the number of tokens in a text.
        Note that this method is not totally accurate, as it does not take into account special tokens of the model.
        For now, we will use it as an approximation.
        """
        if is_prompt:
            text = self.config.system_prompt + text
        return len(self.encoder.encode(text, allowed_special="all"))

    def call_llm(self, prompt: str) -> str:
        return "This is a placeholder response, you should not see this message. If you do, something went wrong."


class DebugLLM(BaseLLM):
    def call_llm(self, prompt: str) -> str:
        return prompt


class OpenAILLM(BaseLLM):
    def __init__(self, config: LLMConfig, llm_cache=None):
        super().__init__(config=config, llm_cache=llm_cache)
        self.client = OpenAI(
            base_url=os.environ.get("OPENAI_API_URL", None),
            api_key=os.environ["OPENAI_API_KEY"],
        )

        # https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
        try:
            self.encoder = tiktoken.encoding_for_model(self.config.model)
        except Exception as e:
            logger.error(
                f"Error when trying to get the encoder for the model,"
                f" falling back to cl100k_base: {e}"
            )
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def call_llm(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        answer = str(response.choices[0].message.content)
        return answer


class LocalTGILLM(BaseLLM):
    """
    Run a local llm, e.g. run mistral-instruct locally:

    docker run --gpus all --shm-size 1g -p 10103:80
    -v /data/hf_tgi_server/models:/data ghcr.io/huggingface/text-generation-inference:1.4
    --model-id mistralai/Mistral-7B-Instruct-v0.2
    --max-input-length 4096 --max-total-tokens=8096

    See tgi documentation: https://huggingface.co/docs/text-generation-inference/index

    WARNING:
        DELETE CACHE DB IF YOU RERUN WITH A DIFFERENT MODEL.
        DB DOES NOT STORE MODEL NAME NOT URL AND IS THUS NOT ABLE TO DIFFERENTIATE BETWEEN MODELS.

        USE CORRECT SYSTEM PROMPT FORMATTING FOR POSSIBLE BETTER RESULTS.
    """

    def __init__(self, config: LLMConfig, llm_cache=None):
        if "TGI_MODEL_URL" not in os.environ:
            raise ValueError("TGI_MODEL_URL not set")
        logger.info(f"Using TGI model: {os.environ['TGI_MODEL_URL']}")
        logger.info(
            "Please see LocalTGILLM class for some caveats when using TGI locally."
        )
        super().__init__(config=config, llm_cache=llm_cache)

    def call_llm(self, prompt: str) -> str:
        client = InferenceClient(model=os.environ["TGI_MODEL_URL"])
        # Can use a special prompt template here for system prompt, if wanted
        # TGI does not yet support chat templates
        result = client.text_generation(
            prompt=self.config.system_prompt + "\n\n" + prompt, max_new_tokens=1024
        )
        return result
