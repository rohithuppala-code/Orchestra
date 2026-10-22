"""LLM API client with tenacity infinite retry."""

from __future__ import annotations

import httpx
from openai import OpenAI
from tenacity import retry, wait_fixed


@retry(wait=wait_fixed(2))
def call_llm(
    api_base: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
) -> dict:
    """Call LLM API and return content + token counts.

    Returns:
        {"content": str, "input_tokens": int, "output_tokens": int}

    Retries indefinitely with 2-second intervals on any failure.
    """
    client = OpenAI(base_url=api_base, api_key=api_key, timeout=httpx.Timeout(3600.0))
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    content_chunks: list[str] = []
    reasoning_chunks: list[str] = []
    input_tokens = 0
    output_tokens = 0
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                content_chunks.append(delta.content)
            reasoning = getattr(delta, "reasoning_content", None)
            if not reasoning and hasattr(delta, "model_extra") and delta.model_extra:
                reasoning = delta.model_extra.get("reasoning_content")
            if reasoning:
                reasoning_chunks.append(reasoning)
        if hasattr(chunk, "usage") and chunk.usage:
            input_tokens = chunk.usage.prompt_tokens or input_tokens
            output_tokens = chunk.usage.completion_tokens or output_tokens
            
    content = "".join(content_chunks)
    if not content and reasoning_chunks:
        content = "".join(reasoning_chunks)
    if output_tokens == 0:
        output_tokens = max(1, len(content) // 4)
    if input_tokens == 0:
        input_tokens = max(1, sum(len(m.get("content", "")) for m in messages) // 4)
        
    return {
        "content": content,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
