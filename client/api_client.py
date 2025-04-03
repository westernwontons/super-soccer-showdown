import abc
import logging
from typing import Any, cast
import asyncio
import os
import json

import httpx


class ApiClient(abc.ABC):
    def __init__(
        self,
        url: str,
        transport: httpx.AsyncBaseTransport | None = None,
        cache_file: str | None = None,
        max_retries: int = 10,
        backoff: int = 2,
    ) -> None:
        self.url = url
        self.client = httpx.AsyncClient(transport=transport)
        self.cache_file = cache_file
        self.max_retries = max_retries
        self.backoff = backoff
        self._results = []

    @property
    def has_cache(self) -> bool:
        return (
            self.cache_file is not None
            and os.path.exists(self.cache_file)
            and os.path.getsize(self.cache_file) > 0
        )

    @property
    def results(self) -> list[dict[str, Any]]:
        if self.cache_file is not None and os.path.exists(self.cache_file):
            with open(self.cache_file) as f:
                return json.load(f)

        return self._results

    def get_cache(self) -> list[dict[str, Any]]:
        if self.cache_file and os.path.exists(self.cache_file):
            with open(self.cache_file) as f:
                return json.load(f)
        return []

    def set_cache(self) -> None:
        if self.cache_file:
            with open(self.cache_file, "w") as f:
                json.dump(self._results, f)

    def next_url(self, data: Any) -> str | None:
        raise NotImplementedError

    async def extract_results(self, data: Any) -> list[dict[str, Any]]:
        raise NotImplementedError

    async def fetch_all(self) -> list[dict[str, Any]]:
        if cache := self.get_cache():
            return cache

        url = self.url

        while url:
            retries = 0
            while retries <= self.max_retries:
                try:
                    response = await self.client.get(cast(str, url))
                    response.raise_for_status()
                    data = response.json()
                    url = self.next_url(data)
                    results = await self.extract_results(data)
                    self._results.extend(results)
                    break
                except (httpx.HTTPError, httpx.ConnectError, httpx.ConnectTimeout) as err:
                    logging.error(f"Error fetching from API: {err}")
                    await asyncio.sleep(self.backoff**retries)
                    retries += 1
            else:
                logging.info(f"Retry limit reached: {self.max_retries}")
                break

        self.set_cache()

        return self._results
