import asyncio
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Dict, Union, Literal
from claudetools.completion.complete import Complete
from claudetools.completion.async_complete import AsyncComplete
from claudetools.extract.single import extractSingleFunction
from claudetools.extract.multiple import extractMultipleFunctions
from claudetools.prompts.multi_functions import MULTI_FUNCTION_CALLS_OPEN_ENDED
from claudetools.prompts.single_function import SINGLE_FUNCTION_OPEN_ENDED, SINGLE_FUNCTION_SPECIFIC_CALL


class FunctionSchema(BaseModel):
    name: str
    description: str
    parameters: Dict


class Functions(BaseModel):
    functions: List[FunctionSchema]


class ToolChoice(BaseModel):
    name: str


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class Messages(BaseModel):
    messages: List[Message]


class BaseTool(ABC):

    async def tool_call(self,
                        model: str,
                        messages: List[Dict],
                        tools: List,
                        tool_choice: Union[None, Dict] = None,
                        multiple_tools=False,
                        attach_system: Union[None, str] = None,
                        **kwargs):
        Messages.model_validate({"messages": messages})
        Functions.model_validate({"functions": tools})
        if multiple_tools:
            system = MULTI_FUNCTION_CALLS_OPEN_ENDED.format(functions=tools)
        else:
            if tool_choice:
                ToolChoice.model_validate(tool_choice)
                tool_name = tool_choice.get("name")
                # print(tool_choice, type(tool_choice))
                system = SINGLE_FUNCTION_SPECIFIC_CALL.format(
                    functions=tools, function_name=tool_name)
            else:
                system = SINGLE_FUNCTION_OPEN_ENDED.format(functions=tools)
        if attach_system:
            system += f"\n\nTask: {attach_system}"
        output = await self.perform_model_call(model,
                                               messages,
                                               system=system,
                                               **kwargs)
        if multiple_tools:
            function_output = extractMultipleFunctions(output)
        else:
            function_output = extractSingleFunction(output)
        return function_output

    @abstractmethod
    async def perform_model_call(self, model, messages, system, **kwargs):
        pass


class Tool(BaseTool):

    def __init__(self,
                 anthropic_api_key: Union[str, None] = None,
                 aws_access_key: Union[str, None] = None,
                 aws_secret_key: Union[str, None] = None,
                 aws_region: Union[str, None] = None,
                 aws_session_token: Union[str, None] = None):
        self.complete = Complete(anthropic_api_key=anthropic_api_key,
                                 aws_secret_key=aws_secret_key,
                                 aws_access_key=aws_access_key,
                                 aws_region=aws_region,
                                 aws_session_token=aws_session_token)

    async def perform_model_call(self, model, messages, system, **kwargs):
        return self.complete(model, messages, system=system, **kwargs)

    def __call__(self,
                 model: str,
                 messages: List[Dict],
                 tools: List,
                 tool_choice: Union[None, Dict] = None,
                 multiple_tools=False,
                 attach_system: Union[None, str] = None,
                 **kwargs):
        return asyncio.run(
            self.tool_call(model, messages, tools, tool_choice, multiple_tools,
                           attach_system, **kwargs))


class AsyncTool(BaseTool):

    def __init__(self,
                 anthropic_api_key: str,
                 anthropic_version: str = "2023-06-01",
                 anthropic_base_url: str = "https://api.anthropic.com/v1"):
        self.complete = AsyncComplete(anthropic_api_key, anthropic_version,
                                      anthropic_base_url)

    async def perform_model_call(self, model, messages, system, **kwargs):
        return await self.complete(model, messages, system=system, **kwargs)

    async def __call__(self,
                       model: str,
                       messages: List[Dict],
                       tools: List,
                       tool_choice: Union[None, Dict] = None,
                       multiple_tools=False,
                       attach_system: Union[None, str] = None,
                       **kwargs):
        return await self.tool_call(model, messages, tools, tool_choice,
                                    multiple_tools, attach_system, **kwargs)


# class Tool:

#     def __init__(self, anthropic_api_key: str):
#         self.complete = Complete(anthropic_api_key)

#     def __call__(self,
#                  model: str,
#                  messages: List[Dict],
#                  tools: List,
#                  tool_choice: Union[None, Dict] = None,
#                  multiple_tools=False,
#                  attach_system: Union[None, str] = None,
#                  **kwargs):
#         Messages.model_validate({"messages": messages})
#         Functions.model_validate({"functions": tools})
#         if multiple_tools:
#             system = MULTI_FUNCTION_CALLS_OPEN_ENDED.format(functions=tools)
#         else:
#             if tool_choice:
#                 ToolChoice.model_validate(tool_choice)
#                 system = SINGLE_FUNCTION_SPECIFIC_CALL.format(
#                     functions=tools, function_name=tool_choice.get("name"))
#             else:
#                 system = SINGLE_FUNCTION_OPEN_ENDED.format(functions=tools)
#         if attach_system:
#             system += f"\n\nTask: {attach_system}"
#         output = self.complete(model, messages, system=system, **kwargs)
#         if multiple_tools:
#             function_output = extractMultipleFunctions(output)
#         else:
#             function_output = extractSingleFunction(output)
#         return function_output

# class AsyncTool:

#     def __init__(self,
#                  anthropic_api_key: str,
#                  anthropic_version: str = "2023-06-01",
#                  anthropic_base_url: str = "https://api.anthropic.com/v1"):
#         self.complete = AsyncComplete(anthropic_api_key, anthropic_version,
#                                       anthropic_base_url)

#     async def __call__(self,
#                        model: str,
#                        messages: List[Dict],
#                        tools: List,
#                        tool_choice: Union[None, Dict] = None,
#                        multiple_tools=False,
#                        attach_system: Union[str, None] = None,
#                        **kwargs):
#         Messages.model_validate({"messages": messages})
#         Functions.model_validate({"functions": tools})
#         if multiple_tools:
#             system = MULTI_FUNCTION_CALLS_OPEN_ENDED.format(functions=tools)
#         else:
#             if tool_choice:
#                 ToolChoice.model_validate(tool_choice)
#                 system = SINGLE_FUNCTION_SPECIFIC_CALL.format(
#                     functions=tools, function_name=tool_choice.get("name"))
#             else:
#                 system = SINGLE_FUNCTION_OPEN_ENDED.format(functions=tools)
#         if attach_system:
#             system += f"\n\nTask: {attach_system}"
#         output = await self.complete(model, messages, system=system, **kwargs)
#         if multiple_tools:
#             function_output = extractMultipleFunctions(output)
#         else:
#             function_output = extractSingleFunction(output)
#         return function_output
