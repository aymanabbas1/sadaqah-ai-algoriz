from __future__ import annotations

from typing import Any

import httpx


class SupabaseDataError(RuntimeError):
    def __init__(self, status_code: int, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code


class SupabaseDataClient:
    def __init__(self, data_api_url: str, secret_key: str) -> None:
        self.data_api_url = data_api_url.rstrip("/")
        self._client = httpx.AsyncClient(
            headers={
                "apikey": secret_key,
                "Accept": "application/json",
                "User-Agent": "sadaqah-intelligence-backend/1.0",
            },
            timeout=30,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def select(self, table: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        response = await self._client.get(f"{self.data_api_url}/{table}", params=params)
        payload = self._decode(response)
        if not isinstance(payload, list):
            raise SupabaseDataError(response.status_code, f"Expected a list from {table}")
        return payload

    async def insert(self, table: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not records:
            return []
        response = await self._client.post(
            f"{self.data_api_url}/{table}",
            json=records,
            headers={"Prefer": "return=representation"},
        )
        payload = self._decode(response)
        return payload if isinstance(payload, list) else []

    async def upsert(
        self,
        table: str,
        records: list[dict[str, Any]],
        on_conflict: str,
    ) -> list[dict[str, Any]]:
        if not records:
            return []
        response = await self._client.post(
            f"{self.data_api_url}/{table}",
            params={"on_conflict": on_conflict},
            json=records,
            headers={"Prefer": "resolution=merge-duplicates,return=representation"},
        )
        payload = self._decode(response)
        return payload if isinstance(payload, list) else []

    async def delete(self, table: str, params: dict[str, Any]) -> None:
        response = await self._client.delete(
            f"{self.data_api_url}/{table}",
            params=params,
            headers={"Prefer": "return=minimal"},
        )
        self._decode(response)

    async def update(self, table: str, values: dict[str, Any], params: dict[str, Any]) -> None:
        response = await self._client.patch(
            f"{self.data_api_url}/{table}",
            params=params,
            json=values,
            headers={"Prefer": "return=minimal"},
        )
        self._decode(response)

    @staticmethod
    def _decode(response: httpx.Response) -> Any:
        if response.is_success:
            if not response.content:
                return None
            return response.json()
        try:
            detail = response.json()
            message = detail.get("message") or detail.get("hint") or response.reason_phrase
            code = detail.get("code")
        except ValueError:
            message = response.reason_phrase
            code = None
        raise SupabaseDataError(response.status_code, message, code)
