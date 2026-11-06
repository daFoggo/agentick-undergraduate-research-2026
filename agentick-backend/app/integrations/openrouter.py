import httpx

from app.core.exceptions import ExternalServiceError

BASE_URL = "https://openrouter.ai/api/v1"
# USD per million tokens (input, output): sent with every request as a price cap, so a model that
# got more expensive is refused instead of billed
PRICE_CAP = {"openai/gpt-6-luna": (0.10, 0.50), "openai/gpt-oss-120b": (0.05, 0.20)}


class OpenRouterChat:
    """One chat completion with tools. Callers only see AppError subclasses; the key and the
    response body never reach a message."""

    def __init__(
        self,
        api_key: str,
        model: str,
        budget: float,
        transport: httpx.BaseTransport | None = None,
    ):
        if model not in PRICE_CAP:
            raise ValueError(f"No price cap known for model {model}")
        self.model, self.budget, self.spent = model, budget, 0.0
        self._http = httpx.Client(
            timeout=60, transport=transport, headers={"Authorization": f"Bearer {api_key}"}
        )

    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        """The assistant message (with its `usage` cost added up in `spent`)."""
        if self.spent >= self.budget:
            raise ExternalServiceError("The assistant has used up its budget.")
        cap = dict(zip(("prompt", "completion"), PRICE_CAP[self.model], strict=True))
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
            "temperature": 0,
            "max_tokens": 700,
            "stream": False,
            "reasoning": {"enabled": False},
            "provider": {"max_price": cap},
        }
        try:
            response = self._http.post(f"{BASE_URL}/chat/completions", json=payload)
            response.raise_for_status()
            body = response.json()
            self.spent += float((body.get("usage") or {}).get("cost") or 0)
            return body["choices"][0]["message"]
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            raise ExternalServiceError("The language model could not be reached.") from exc
