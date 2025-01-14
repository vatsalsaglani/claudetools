[![Downloads](https://static.pepy.tech/badge/claudetools)](https://pepy.tech/project/claudetools)

# Claudetools

**Claudetools** is a Python library that provides a convenient way to use Claude 3 family's structured data generation capabilities for function calling. The function calling capabilities are similar to ones available with OpenAI models.

With `claudetools` one can now use any model from the **Claude 3** family of models for function calling.

## Key Features

- **Function Calling**: Define and call custom functions within your prompts, leveraging the advanced capabilities of Claude 3 models.
- **Synchronous and Asynchronous Clients**: Choose between synchronous or asynchronous interaction modes depending on your use case.
- **Flexible Tool Definition**: Specify function names, descriptions, and parameters using the Pydantic library for type safety and validation.
- **Multiple Tools Support**: Opt to call multiple tools within a single prompt, enabling more complex interactions.
- **Customizable System Prompts**: Attach custom system prompts to your conversations for better context and control.
- **Bedrock Client**: Use Claude 3 via AWS Bedrock for function calling.


## Installation

You can install `claudetools` from PyPI or directly from the source:

### From PyPi

```bash
pip install claudetools
```

### Install from source

```bash
pip install git+https://github.com/vatsalsaglani/claudetools
```

## Usage

Here's a basic example of how to use `claudetools` for function calling with the Claude 3 model:

```py
import asyncio
from claudetools.tools.tool import Tool
from pydantic import BaseModel, Field
from typing import List, Dict
import json

# create a tool instance with your Anthropic API Key
tool = Tool(ANTHROPIC_API_KEY)

# define your function parameters
class AddTodo(BaseModel):
    text: str = Field(..., description="Text to add for the TODO to remember.")

class MarkCompleted(BaseModel):
    text: str = Field(..., description="Text of the completed TODO.")


class ReOpen(BaseModel):
    text: str = Field(..., description="Text of the TODO to reopen.")


# specify the functions you want to use
functions = [{
    "name": "AddTodo",
    "description": "Add a TODO with text to remember.",
    "parameters": AddTodo.model_json_schema()
}, {
    "name": "MarkCompleted",
    "description": "Get text of the todo mark it complete",
    "parameters": MarkCompleted.model_json_schema()
}, {
    "name": "ReOpen",
    "description": "Get text of the todo reopen it.",
    "parameters": ReOpen.model_json_schema()
}]

# set up the user messages
user_messages = [{
    "role":
    "user",
    "content":
    """I have to pick up my daughter from school. After which I've to do the laundary. And now I need to cook lunch."""
}]

# dependency prompt to attach to the main system prompt
DEPENDENCY_PROMPT = """You are a helpful assistant that helps a user with their tasks and todos. The user can add a todos, mark todos as completed, or reopen certain todos.
The user can provide multiple actions at once so you've to break those down and call the appropriate functions in the correct sequence."""


# call the tool with the required parameters
output = tool(model="claude-3-sonnet-20240229",
              messages=user_messages,
              tools=functions,
              tool_choice=None,
              multiple_tools=True,
              attach_system=DEPENDENCY_PROMPT,
              max_tokens=3000)

if output:
    print(json.dumps(output, indent=4))
else:
    print("Unable to find a function!")
```

> No default value of `max_tokens` is assumed hence, please provide `max_tokens` to avoid getting an error from the Claude APIs.

_The parameter explanation is provided below._

- `model`: The name of the model from the Claude 3 family.
- `messages`: Messages transferred between the user and the assistant.
- `tools`: Set of function specification to use.
- `tool_choice`: User a particular function. By default the value is `None`. The model will figure out the function to call and provide the related parameters. If a specific function needs to be called provide `{"name": "function name"}` in the `tool_choice` argument.
- `multiple_tools`: Defaults to `False`. Can be set to `True` to get multiple function calls.
- `attach_system`: Defaults to `None`. Can also accept string which will be attached as part of the system prompt.
- `max_tokens`: As mentioned above, no default value of `max_tokens` is assumed. Hence, please provide `max_tokens` to avoid getting an error.


### Asynchronous Interaction

Just import `AsyncTool` instead of `Tool` to and use `await` with each call.

```py
import asyncio
from claudetools.tools.tool import AsyncTool
from pydantic import BaseModel, Field
from typing import List, Dict
import json

tool = AsyncTool(ANTHROPIC_API_KEY)

class AddTodo(BaseModel):
    text: str = Field(..., description="Text to add for the TODO to remember.")


functions = [{
    "name": "AddTodo",
    "description": "Add a TODO with text to remember.",
    "parameters": AddTodo.model_json_schema()
}, {
    "name": "MarkCompleted",
    "description": "Get text of the todo mark it complete",
    "parameters": MarkCompleted.model_json_schema()
}, {
    "name": "ReOpen",
    "description": "Get text of the todo reopen it.",
    "parameters": ReOpen.model_json_schema()
}]

user_messages = [{
    "role":
    "user",
    "content":
    """I have to pick up my daughter from school. After which I've to do the laundary. And now I need to cook lunch."""
}]

async def main():

    output = await tool(model="claude-3-sonnet-20240229",
                messages=user_messages,
                tools=functions,
                tool_choice=None,
                multiple_tools=True,
                attach_system=None,
                max_tokens=3000)
    if output:
        print(json.dumps(output, indent=4))
    else:
        print("Unable to find a function!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Bedrock Example

> Currently, only the sync client supports AWS Bedrock.

```py
import asyncio
from claudetools.tools.tool import Tool
from pydantic import BaseModel, Field
from typing import List, Dict
import json

AWS_ACCESS_KEY=""
AWS_SECRET_KEY=""
AWS_REGION=""
# or
AWS_SESSION_TOKEN=""

# create a tool instance with your aws access and secret keys
tool = Tool(aws_access_key=AWS_ACCESS_KEY,
            aws_secret_key=AWS_SECRET_KEY,
            aws_region=AWS_REGION)
# to use session token from AWS STS use the following
# tool = Tool(aws_session_token=AWS_SESSION_TOKEN, aws_region=AWS_REGION)


# define your function parameters
class AddTodo(BaseModel):
    text: str = Field(..., description="Text to add for the TODO to remember.")

class MarkCompleted(BaseModel):
    text: str = Field(..., description="Text of the completed TODO.")


class ReOpen(BaseModel):
    text: str = Field(..., description="Text of the TODO to reopen.")


# specify the functions you want to use
functions = [{
    "name": "AddTodo",
    "description": "Add a TODO with text to remember.",
    "parameters": AddTodo.model_json_schema()
}, {
    "name": "MarkCompleted",
    "description": "Get text of the todo mark it complete",
    "parameters": MarkCompleted.model_json_schema()
}, {
    "name": "ReOpen",
    "description": "Get text of the todo reopen it.",
    "parameters": ReOpen.model_json_schema()
}]

# set up the user messages
user_messages = [{
    "role":
    "user",
    "content":
    """I have to pick up my daughter from school. After which I've to do the laundary. And now I need to cook lunch."""
}]

# dependency prompt to attach to the main system prompt
DEPENDENCY_PROMPT = """You are a helpful assistant that helps a user with their tasks and todos. The user can add a todos, mark todos as completed, or reopen certain todos.
The user can provide multiple actions at once so you've to break those down and call the appropriate functions in the correct sequence."""


# call the tool with the required parameters
output = tool(model="claude-3-sonnet-20240229",
              messages=user_messages,
              tools=functions,
              tool_choice=None,
              multiple_tools=True,
              attach_system=DEPENDENCY_PROMPT,
              max_tokens=3000)

if output:
    print(json.dumps(output, indent=4))
else:
    print("Unable to find a function!")
```


## Requirements

Python 3.7 or higher.

## TODOs

- [ ] Add examples notebook.
- [ ] Enable logging.
- [ ] Add support for AWS Bedrock.
- [ ] Validate outputs in `tool_choice`.

## Contributing

Contributions to `claudetools` are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on this GitHub repository.
