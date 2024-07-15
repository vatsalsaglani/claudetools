import os
import json
import logging
from typing import List, Dict, Union
from anthropic import AsyncAnthropic, AsyncAnthropicBedrock

logger = logging.getLogger(__name__)

# class AsyncComplete:

#     def __init__(self,
#                  anthropic_api_key: str,
#                  anthropic_version: str = "2023-06-01",
#                  anthropic_base_url: str = "https://api.anthropic.com/v1"):
#         self.headers = {
#             "x-api-key": anthropic_api_key,
#             "anthropic-version": anthropic_version,
#             "content-type": "application/json"
#         }
#         self.anthropic_base_url = anthropic_base_url

#     async def __call__(self, model: str, messages: List[Dict], **kwargs):
#         payload = {
#             **kwargs,
#             "model": model,
#             "messages": messages,
#         }
#         async with httpx.AsyncClient(timeout=600) as client:
#             response = await client.post(os.path.join(self.anthropic_base_url,
#                                                       "messages"),
#                                          json=payload,
#                                          headers=self.headers)
#             response.raise_for_status()
#             output = response.json()
#             # print("MODEL OUTPUT\n", output)
#             return output.get("content")[0].get("text")


class AsyncComplete:

    def __init__(self,
                 anthropic_api_key: Union[str, None] = None,
                 aws_access_key: Union[str, None] = None,
                 aws_secret_key: Union[str, None] = None,
                 aws_region: Union[str, None] = None,
                 aws_session_token: Union[str, None] = None):
        if anthropic_api_key:
            self.client = AsyncAnthropic(api_key=anthropic_api_key)
        else:
            if aws_session_token:
                self.client = AsyncAnthropicBedrock(
                    aws_session_token=aws_session_token, aws_region=aws_region)
            else:
                self.client = AsyncAnthropicBedrock(
                    aws_access_key=aws_access_key,
                    aws_secret_key=aws_secret_key,
                    aws_region=aws_region)

    async def __call__(self, model: str, messages: List[Dict], **kwargs):
        logging.info(f"MODEL: {model}")
        logging.info(
            f"KWARGS: {json.dumps(kwargs, indent=4) if kwargs else 'NONE'}")
        response = await self.client.messages.create(model=model,
                                                     messages=messages,
                                                     **kwargs)
        logging.info(f"RESPONSE: {response}")
        return response.content[0].text
