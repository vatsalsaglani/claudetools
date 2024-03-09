from anthropic import Anthropic
from typing import List, Dict


class Complete:

    def __init__(self, anthropic_api_key: str):
        self.client = Anthropic(api_key=anthropic_api_key)

    def __call__(self, model: str, messages: List[Dict], **kwargs):
        output = self.client.messages.create(model=model,
                                             messages=messages,
                                             **kwargs)
        print("MODEL OUTPUT\n", output)
        return output.content[0].text
