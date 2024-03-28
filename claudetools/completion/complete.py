import json
import logging
from anthropic import Anthropic, AnthropicBedrock
from typing import List, Dict, Union

logger = logging.getLogger(__name__)


class Complete:

    def __init__(self,
                 anthropic_api_key: Union[str, None] = None,
                 aws_access_key: Union[str, None] = None,
                 aws_secret_key: Union[str, None] = None,
                 aws_region: Union[str, None] = None,
                 aws_session_token: Union[str, None] = None):
        if anthropic_api_key:
            self.client = Anthropic(api_key=anthropic_api_key)
        else:

            if aws_session_token:
                self.client = AnthropicBedrock(
                    aws_session_token=aws_session_token, aws_region=aws_region)
            else:
                self.client = AnthropicBedrock(aws_access_key=aws_access_key,
                                               aws_secret_key=aws_secret_key,
                                               aws_region=aws_region)

    def __call__(self, model: str, messages: List[Dict], **kwargs):
        logging.info(f"MODEL: {model}")
        logging.info(
            f"KWARGS: {json.dumps(kwargs, indent=4) if kwargs else 'NONE'}")
        output = self.client.messages.create(model=model,
                                             messages=messages,
                                             **kwargs)
        logging.info(f"RESPONSE: {output}")
        # print("MODEL OUTPUT\n", output)
        return output.content[0].text
