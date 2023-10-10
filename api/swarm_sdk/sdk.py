import asyncio

import aiohttp
from urllib.parse import urljoin
from swarm_sdk.exceptions import BatchIDRequiredException


class SwarmClient:
    def __init__(self, batch_id: str = None, server_url: str = "http://localhost:1633/"):
        self.batch_id = batch_id
        self.server_url = server_url

    def generate_api_url(self):
        url = self.server_url
        if not url.endswith("/bzz"):
            url = urljoin(url, "bzz")
        return url

    async def download(self, file_id: str):
        file_url = f"{self.generate_api_url()}/{file_id}/"
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as response:
                async for ln in response.content.iter_chunked(1024):
                    yield ln
                    await asyncio.sleep(0)

    async def upload(self, stream: any, name: str = None, content_type: str = None):
        if not self.batch_id:
            raise BatchIDRequiredException("Batch ID is required for uploading files")

        content_type = content_type or "application/octet-stream"

        headers = {"Swarm-Postage-Batch-Id": self.batch_id, "Content-Type": content_type}
        api_url = self.generate_api_url()
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, params={"name": name}, headers=headers, data=stream) as response:
                response.raise_for_status()
                return await response.json()

    async def create_batch(self, amount: int, depth: int):
        api_url = urljoin(self.server_url, f"stamps/{amount}/{depth}")
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url) as response:
                response.raise_for_status()
                return await response.json()

    async def get_batch_info(self, batch_id: str):
        api_url = urljoin(self.server_url, f"stamps/{batch_id}")
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                response.raise_for_status()
                return await response.json()
