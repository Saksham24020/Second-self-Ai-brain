import os
from typing import Optional
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from loguru import logger
from src.config import settings

_groq_client = None

def get_llm_client():
    """Create and return cached Groq client."""
    global _groq_client
    if _groq_client is None:
        api_key = settings.LLM_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key:
            return None
        _groq_client = Groq(api_key=api_key)
    return _groq_client

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(Exception))
def chat_completion(prompt: str, json_mode: bool = False, model: Optional[str] = None) -> Optional[str]:
    """Execute chat completion with retry logic."""
    client = get_llm_client()
    if not client:
        return None
    try:
        kwargs = {
            "model": model or settings.LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": settings.RAG_MAX_TOKENS,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"LLM call failed: {e}")
        raise
