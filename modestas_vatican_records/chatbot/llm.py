import asyncio
from pathlib import Path
from typing import Dict, List

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub.errors import HFValidationError

from chatbot.config import (
    ANSWER_SYSTEM_PROMPT,
    GENERAL_SYSTEM_PROMPT,
    HF_CACHE_DIR,
    HF_LLM_MODEL_ID,
    MAX_NEW_TOKENS,
    QUESTIONS_SYSTEM_PROMPT,
    RAG_SYSTEM_PROMPT,
)
from chatbot.utils.logging_config import configure_logging

Logger = configure_logging()


class LLM:

    def __init__(self, pretrained_model_name_or_path: str | Path | None = None):
        """Initializes an LLM instance.

        Args:
            pretrained_model_name_or_path (str | Path | None, optional): The path or name of the pretrained model. Defaults to None.

        Raises:
            OSError: If the model or tokenizer cannot be loaded.
        """

        if not pretrained_model_name_or_path:
            pretrained_model_name_or_path = HF_LLM_MODEL_ID

        Logger.info(
            f"Loading model and tokenizer from {pretrained_model_name_or_path}"
        )
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                pretrained_model_name_or_path, 
                torch_dtype="auto", 
                device_map="auto",
                cache_dir=HF_CACHE_DIR
            )
            self.tokenizer = AutoTokenizer.from_pretrained(
                pretrained_model_name_or_path,
                cache_dir=HF_CACHE_DIR
            )
            self.device: torch.device = self.model.device
            Logger.info(
                f"Model and tokenizer loaded successfully from {pretrained_model_name_or_path}"
            )
        except (OSError, FileNotFoundError, HFValidationError) as e:
            Logger.error(f"Error loading model or tokenizer: {e}")
            raise


    async def chat(
        self,
        user_prompt: str,
        conversation_history: List[Dict[str, str]] | None = None,
        system_prompt: str | None = None,
    ) -> str:
        """Generates a chat response using the language model.

        Args:
            user_prompt (str): The user's prompt.
            conversation_history (List[Dict[str, str]] | None, optional): The conversation history. Defaults to None.
            system_prompt (str | None, optional): The system prompt. Defaults to None.

        Returns:
            str: The generated chat response.

        Raises:
            Exception: If there is an error during text generation.
        """

        if not conversation_history:
            conversation_history = []

        if not system_prompt:
            system_prompt = GENERAL_SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history,
            {"role": "user", "content": user_prompt},
        ]

        text = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        try:
            generated_ids = await asyncio.to_thread(
                self.model.generate, **model_inputs, max_new_tokens=MAX_NEW_TOKENS
            )
            generated_ids = [
                output_ids[len(input_ids) :]
                for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]
            return response
        except Exception as e:
            Logger.error(f"Error during text generation: {e}")
            raise

    async def rag(
        self,
        query: str,
        documents: List[str],
        conversation_history: List[Dict[str, str]] | None = None,
    ) -> str:
        """Performs Retrieval Augmented Generation (RAG) to answer a query using provided documents.

        Args:
            query (str): The user's query.
            documents (List[str]): A list of relevant documents.
            conversation_history (List[Dict[str, str]] | None, optional): The conversation history. Defaults to None.

        Returns:
            str: The generated RAG response.
        """

        context_information = "\\n\\n".join(documents)
        user_prompt = f"Question: {query}. \\n Information: {context_information}"
        return await self.chat(
            user_prompt=user_prompt,
            conversation_history=conversation_history,
            system_prompt=RAG_SYSTEM_PROMPT,
        )

    async def expand_querry_question(
        self, user_prompt: str
    ) -> List[str]:
        """Expands the user's query question by generating additional related questions.

        Args:
            user_prompt (str): The initial user prompt or query.

        Returns:
            List[str]: A list of strings, where the first element is the original `user_prompt` and
                subsequent elements are the generated related questions.
        """

        additional_prompt = await self.chat(
            user_prompt=user_prompt, system_prompt=QUESTIONS_SYSTEM_PROMPT
        )
        return [user_prompt] + additional_prompt.split("\n")
    
    async def generate_a_help_answer_query(
        self, user_prompt: str
    ) -> str:
        """Generates a helper answer to the user's query.
        Args:
            user_prompt (str): The initial user prompt or query.

        Returns:
            str: A string containing the original user prompt and the generated helpful answer, separated by a newline.
        """

        helper_answer = await self.chat(
            user_prompt=user_prompt, system_prompt=ANSWER_SYSTEM_PROMPT
        )
        return "\n".join([user_prompt, helper_answer])