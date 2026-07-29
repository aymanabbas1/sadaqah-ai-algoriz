from __future__ import annotations

import json
from typing import Any

from openai import AsyncOpenAI

from app.core.config import Settings
from app.schemas import ChatRequest, ToolResult
from app.services.tools import ToolEngine


GREETING_PROMPT = """You are Mansa Musa, the contextual research assistant for Sadaqah Intelligence Platform.
Reply warmly and briefly to the greeting. Do not introduce humanitarian facts, recommendations, or statistics."""

FINAL_PROMPT = """You are Mansa Musa. A deterministic research tool has completed the request.
Write a concise answer using only the supplied JSON. Do not rank crises, recommend NGOs, choose a winner, or introduce claims absent from the result.
For crisis context, keep the selected crisis central to the answer. For NGO comparison context, discuss only the selected NGO profiles and use the crisis only as location context; never substitute a crisis summary for the NGO comparison.
Mention that the user can open the attached official sources when useful. Keep the answer below 100 words."""


class LlmOrchestrator:
    def __init__(self, settings: Settings, tools: ToolEngine) -> None:
        self.settings = settings
        self.tools = tools
        self.client: AsyncOpenAI | None = None
        self.model = settings.llm_model

        if settings.llm_provider == "openai" and settings.openai_api_key:
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
            self.model = self.model or "gpt-4.1-mini"
        elif settings.llm_provider == "groq" and settings.groq_api_key:
            self.client = AsyncOpenAI(api_key=settings.groq_api_key, base_url="https://api.groq.com/openai/v1")
            self.model = self.model or "openai/gpt-oss-20b"

    @property
    def configured(self) -> bool:
        return self.client is not None

    async def greet(self, request: ChatRequest) -> str:
        if self.client is None:
            raise RuntimeError("LLM provider is not configured")

        messages: list[dict[str, Any]] = [{"role": "system", "content": GREETING_PROMPT}]
        messages.extend({"role": item.role, "content": item.content} for item in request.conversation[-8:])
        messages.append({"role": "user", "content": request.message})
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or "Hello. What would you like to investigate?"

    async def explain(self, request: ChatRequest, result: ToolResult) -> str:
        if self.client is None:
            raise RuntimeError("LLM provider is not configured")

        final = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": FINAL_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Screen context: {request.contextType}\n"
                        f"Selected crisis ID: {request.crisisId}\n"
                        f"Selected NGO IDs: {', '.join(request.ngoIds) or 'none'}\n"
                        f"Original request: {request.message}\n\n"
                        f"Completed tool result:\n{json.dumps(result.model_dump(mode='json'), default=str)}"
                    ),
                },
            ],
            temperature=0.2,
        )
        return final.choices[0].message.content or "I found the sourced profile but could not summarize it."
