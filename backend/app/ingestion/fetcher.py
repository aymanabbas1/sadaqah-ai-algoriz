from __future__ import annotations

import asyncio
import hashlib
import io
import re

import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.ingestion.models import FetchResult


class OfficialSourceClient:
    def __init__(self) -> None:
        self._client = httpx.AsyncClient(
            headers={
                "User-Agent": "SadaqahIntelligence/1.0 (+official-source-refresh)",
                "Accept": "application/json,text/html,application/pdf;q=0.9,*/*;q=0.5",
            },
            follow_redirects=True,
            timeout=60,
            limits=httpx.Limits(max_connections=5, max_keepalive_connections=5),
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch(
        self,
        url: str,
        etag: str | None = None,
        last_modified: str | None = None,
    ) -> FetchResult:
        headers: dict[str, str] = {}
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified

        for attempt in range(3):
            try:
                response = await self._client.get(url, headers=headers)
                if response.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                if response.status_code == 304:
                    return FetchResult(
                        url=url,
                        status=304,
                        etag=response.headers.get("etag") or etag,
                        last_modified=response.headers.get("last-modified") or last_modified,
                    )
                if not response.is_success:
                    return FetchResult(url=url, status=response.status_code, error=response.reason_phrase)
                content = response.content
                content_type = response.headers.get("content-type", "").lower()
                text = self._extract_pdf(content) if "pdf" in content_type or url.lower().endswith(".pdf") else self._extract_html(response.text)
                return FetchResult(
                    url=str(response.url),
                    status=response.status_code,
                    content=content,
                    text=text,
                    content_hash=hashlib.sha256(content).hexdigest(),
                    etag=response.headers.get("etag"),
                    last_modified=response.headers.get("last-modified"),
                )
            except (httpx.HTTPError, ValueError) as exc:
                if attempt < 2:
                    await asyncio.sleep(1.5 * (attempt + 1))
                    continue
                return FetchResult(url=url, status=0, error=f"{type(exc).__name__}: {exc}")
        return FetchResult(url=url, status=0, error="Source fetch failed")

    @staticmethod
    def _extract_html(html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        for node in soup(["script", "style", "noscript", "svg"]):
            node.decompose()
        return re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        text = " ".join(page.extract_text() or "" for page in reader.pages)
        return re.sub(r"\s+", " ", text).strip()
