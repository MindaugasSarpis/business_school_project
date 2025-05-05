import os
from typing import List, Tuple

import google
import google.generativeai as genai
from dotenv import load_dotenv

from chatbot.utils.logging_config import configure_logging
from tests.core.evaluation_prompt_template import (
    EVALUATION_PROMPT,
    FEEDBACK_GENERALIZATION_PROMPT,
)

load_dotenv()
Logger = configure_logging()


class EvaluatorLLM:
    def __init__(self) -> None:
        """Initializes the EvaluatorLLM with the Gemini API key and model."""

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(os.getenv("GEMINI_MODEL"))
        self.gemini_chat = self.model.start_chat()

    async def chat(self, prompt: str) -> str:
        """Sends a message to the Gemini chat model and returns the response.

        Args:
            prompt (str): The prompt to send to the model.

        Returns:
            str: The model's response.

        Raises:
            google.api_core.exceptions.ResourceExhausted: If the API rate limit is exceeded.
        """

        try:
            response = await self.gemini_chat.send_message_async(prompt)
            return response.text
        except google.api_core.exceptions.ResourceExhausted as e:
            Logger.error(f"llm_completion RateLimitError: {e.status_code} {e.message}")
            raise

    async def evaluate(
        self, query: str, response: str, expected_response: str
    ) -> Tuple[str, str]:
        """Evaluates a response against an expected response using the evaluation prompt.

        Args:
            query (str): The original query.
            response (str): The response to evaluate.
            expected_response (str): The expected response.

        Returns:
            Tuple[str, str]: A tuple containing the feedback and the score.
        """

        eval_prompt = EVALUATION_PROMPT.format(
            instruction=query,
            response=response,
            reference_answer=expected_response,
        )

        eval_result = await self.chat(eval_prompt)
        feedback, score = [item.strip() for item in eval_result.split("[RESULT]")]

        return feedback, score

    async def generalize_feedback(self, feedback_acc: List[str]) -> str:
        """Generalizes a list of feedback strings into a single summary.

        Args:
            feedback_acc (List[str]): A list of feedback strings.

        Returns:
            str: A generalized feedback summary.
        """

        full_feedback = "\n".join(feedback_acc)
        feedback_eval_prompt = FEEDBACK_GENERALIZATION_PROMPT.format(
            feedback=full_feedback
        )

        return await self.chat(feedback_eval_prompt)
