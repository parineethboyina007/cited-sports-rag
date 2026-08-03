from __future__ import annotations

import os
from abc import ABC, abstractmethod

from groq import Groq

from app.config import GROQ_MODEL, LLM_MAX_TOKENS, LLM_TEMPERATURE


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate response from the LLM."""
        pass


class GroqClient(LLMClient):
    def __init__(self):
        # Always use the environment variable
        api_key = os.environ.get("GROQ_API_KEY", "")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is missing.")
        self.client = Groq(api_key=api_key)
        self.model = GROQ_MODEL

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            messages=messages,
            model=self.model,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
        )
        
        content = response.choices[0].message.content
        return content if content else ""
