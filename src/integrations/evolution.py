import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class EvolutionClient:
    def __init__(
        self,
        api_url: str | None,
        instance: str | None,
        api_key: str | None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._api_url = api_url
        self._instance = instance
        self._api_key = api_key
        self._http_client = http_client

    @property
    def configured(self) -> bool:
        return bool(self._api_url and self._instance and self._api_key)

    @retry(wait=wait_exponential(min=1, max=4), stop=stop_after_attempt(3), reraise=True)
    async def send_text(self, phone_number: str, text: str) -> dict[str, Any]:
        if not self.configured:
            logger.info(
                "Evolution client not configured; skipping outbound send",
                extra={"phone_number": phone_number, "event_type": "outbound_skipped"},
            )
            return {"status": "skipped", "message": text}

        client = self._http_client or httpx.AsyncClient()
        should_close = self._http_client is None
        try:
            headers: dict[str, str] = {
                "Content-Type": "application/json",
                "apikey": self._api_key or "",
            }
            response = await client.post(
                f"{self._api_url}/message/sendText/{self._instance}",
                json={"number": phone_number, "textMessage": {"text": text}},
                headers=headers,
                timeout=15.0,
            )
            response.raise_for_status()
            return dict(response.json())
        finally:
            if should_close:
                await client.aclose()
