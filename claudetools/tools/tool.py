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
import logging

logger = logging.getLogger(__name__)


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
    content: Union[str, List, List[Dict]]


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
                        validate_params: bool = True,
                        force_tool_call: bool = True,
                        max_retries: int = 3,
                        **kwargs):
        Messages.model_validate({"messages": messages})
        Functions.model_validate({"functions": tools})

        # Set up system prompt
        if multiple_tools:
            system = MULTI_FUNCTION_CALLS_OPEN_ENDED.format(functions=tools)
        else:
            if tool_choice:
                ToolChoice.model_validate(tool_choice)
                tool_name = tool_choice.get("name")
                system = SINGLE_FUNCTION_SPECIFIC_CALL.format(
                    functions=tools, function_name=tool_name)
            else:
                system = SINGLE_FUNCTION_OPEN_ENDED.format(functions=tools)

        if attach_system:
            system += f"\n\nTask: {attach_system}"

        # Handle retries if force_tool_call is enabled
        retries = 0
        while retries < max_retries:
            logger.info(f"Attempt {retries + 1} of {max_retries}")
            output = await self.perform_model_call(model,
                                                   messages,
                                                   system=system,
                                                   **kwargs)

            if multiple_tools:
                function_output = extractMultipleFunctions(output)
            else:
                function_output = extractSingleFunction(output)
                # For single tool mode, take only the first function
                function_output = function_output[
                    0] if function_output else None

            # If we got a function call(s), validate it/them
            if function_output:
                if multiple_tools:
                    if not isinstance(function_output, list):
                        function_output = [function_output]
                else:
                    if not function_output:
                        if force_tool_call and retries < max_retries - 1:
                            logger.warning(
                                "No valid function call found in output. Retrying..."
                            )
                            retries += 1
                            continue
                        else:
                            return output if not force_tool_call else None

                    # Check if the selected tool matches tool_choice for single tool mode
                    if tool_choice:
                        selected_tool = function_output.get('name')
                        required_tool = tool_choice.get('name')
                        if selected_tool != required_tool:
                            if force_tool_call and retries < max_retries - 1:
                                logger.warning(
                                    f"Tool mismatch: got '{selected_tool}', expected '{required_tool}'. Retrying..."
                                )
                                system += f"\n\nYou must use the specified function '{required_tool}'. Please try again."
                                retries += 1
                                continue
                            else:
                                raise ValueError(
                                    f"Selected tool '{selected_tool}' does not match required tool '{required_tool}'"
                                )

                # Validate parameters if needed
                if validate_params:
                    validation_errors = self._validate_parameters(
                        function_output, tools)
                    if validation_errors:
                        if force_tool_call and retries < max_retries - 1:
                            logger.warning(
                                f"Parameter validation failed: {validation_errors}. Retrying..."
                            )
                            system += f"\n\nYour previous response had validation errors: {validation_errors}. Please try again with valid parameters."
                            retries += 1
                            continue
                        else:
                            raise ValueError(
                                f"Parameter validation failed: {validation_errors}"
                            )
                return function_output

            # No function call detected
            elif force_tool_call and retries < max_retries - 1:
                logger.warning("No function call detected. Retrying...")
                system += "\n\nYou must select an appropriate function to call. Please try again."
                retries += 1
                continue
            else:
                if force_tool_call:
                    logger.error(
                        "Maximum retries reached without valid function call")
                    raise ValueError(
                        "No valid function call detected after maximum retries"
                    )
                return output  # Return raw output when no function call and force_tool_call is False

        return None

    def _validate_parameters(self, function_output: Union[Dict, List[Dict]],
                             tools: List[Dict]) -> List[str]:
        """Validate parameters against function schemas."""
        validation_errors = []

        if isinstance(function_output, dict):
            function_output = [function_output]

        for call in function_output:
            function_name = call.get('name')
            parameters = call.get('parameters', {})

            # Find matching function schema
            function_schema = next(
                (t for t in tools if t['name'] == function_name), None)
            if not function_schema:
                validation_errors.append(f"Unknown function: {function_name}")
                continue

            # Validate required parameters
            required_params = function_schema.get('parameters',
                                                  {}).get('required', [])
            for param in required_params:
                if param not in parameters:
                    validation_errors.append(
                        f"Missing required parameter '{param}' for function '{function_name}'"
                    )

            # Validate parameter types
            properties = function_schema.get('parameters',
                                             {}).get('properties', {})
            for param_name, param_value in parameters.items():
                if param_name not in properties:
                    validation_errors.append(
                        f"Unexpected parameter '{param_name}' for function '{function_name}'"
                    )
                    continue

                expected_type = properties[param_name].get('type')
                if not self._check_type(param_value, expected_type):
                    validation_errors.append(
                        f"Parameter '{param_name}' for function '{function_name}' should be of type {expected_type}"
                    )

        return validation_errors

    def _check_type(self, value, expected_type: str) -> bool:
        """Check if value matches expected type."""
        type_checks = {
            'string': lambda x: isinstance(x, str),
            'number': lambda x: isinstance(x, (int, float)),
            'integer': lambda x: isinstance(x, int),
            'boolean': lambda x: isinstance(x, bool),
            'array': lambda x: isinstance(x, list),
            'object': lambda x: isinstance(x, dict)
        }
        return type_checks.get(expected_type, lambda x: True)(value)

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
                 anthropic_api_key: Union[str, None] = None,
                 aws_access_key: Union[str, None] = None,
                 aws_secret_key: Union[str, None] = None,
                 aws_region: Union[str, None] = None,
                 aws_session_token: Union[str, None] = None):
        # self.complete = AsyncComplete(anthropic_api_key, anthropic_version,
        #                               anthropic_base_url)
        self.complete = AsyncComplete(anthropic_api_key=anthropic_api_key,
                                      aws_secret_key=aws_secret_key,
                                      aws_access_key=aws_access_key,
                                      aws_region=aws_region,
                                      aws_session_token=aws_session_token)

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
