import httpx

from app.config import get_settings

SYSTEM_PROMPT = """You are Atlas, a local HomeLab assistant. State only supported
findings, explain uncertainty, and recommend safe operational next steps."""


class OllamaService:
    async def check_ready(self) -> None:
        settings = get_settings()
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{settings.ollama_base_url}/api/tags")
            response.raise_for_status()

    async def chat(self, message: str) -> str:
        settings = get_settings()
        payload = {
            "model": settings.ollama_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{settings.ollama_base_url}/api/chat", json=payload)
            response.raise_for_status()
        return response.json()["message"]["content"]
