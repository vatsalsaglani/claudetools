import httpx
import os
from typing import List, Dict


class AsyncComplete:

    def __init__(self,
                 anthropic_api_key: str,
                 anthropic_version: str = "2023-06-01",
                 anthropic_base_url: str = "https://api.anthropic.com/v1"):
        self.headers = {
            "x-api-key": anthropic_api_key,
            "anthropic-version": anthropic_version,
            "content-type": "application/json"
        }
        self.anthropic_base_url = anthropic_base_url

    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        payload = {
            **kwargs,
            "model": model,
            "messages": messages,
        }
        async with httpx.AsyncClient(timeout=600) as client:
            response = await client.post(os.path.join(self.anthropic_base_url,
                                                      "messages"),
                                         json=payload,
                                         headers=self.headers)
            response.raise_for_status()
            output = response.json()
            # print("MODEL OUTPUT\n", output)
            return output.get("content")[0].get("text")
