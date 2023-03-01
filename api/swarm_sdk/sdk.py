import io
import mimetypes
from urllib.parse import urljoin

import requests


class SwarmClient:
    def __init__(self, batch_id: str = None, server_url: str = "http://localhost:1633/"):
        self.batch_id = batch_id
        self.server_url = server_url

    def generate_api_url(self):
        url = self.server_url
        if not url.endswith("/bzz"):
            url = urljoin(url, "bzz")
        return url

    def download(self, file_id: str):
        file_url = f"{self.generate_api_url()}/{file_id}/"
        response = requests.get(file_url)
        response.raise_for_status()
        return response.content

    def upload(self, file: str | bytes, name: str = None, content_type: str = None):
        headers = {}
        assert self.batch_id
        headers["Swarm-Postage-Batch-Id"] = self.batch_id
        file_obj = None
        if isinstance(file, str):
            file_obj = open(file, "rb")
            content_type = content_type or mimetypes.guess_type(file)[0]
        elif isinstance(file, bytes):
            file_obj = io.BytesIO(file)
        content_type = content_type or "application/octet-stream"
        headers["Content-Type"] = content_type
        api_url = self.generate_api_url()
        response = requests.post(api_url, params={"name": name}, headers=headers, data=file_obj)
        response.raise_for_status()
        return response.json()
