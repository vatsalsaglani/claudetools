import asyncio
from configs import ANTHROPIC_API_KEY
from pydantic import BaseModel, Field
from typing import List, Dict
import json
from claudetools.tools.tool import Tool, AsyncTool

tool = Tool(ANTHROPIC_API_KEY)


class AddTodo(BaseModel):
    text: str = Field(..., description="Text to add for the TODO to remember.")


class MarkCompleted(BaseModel):
    text: str = Field(..., description="Text of the completed TODO.")


class ReOpen(BaseModel):
    text: str = Field(..., description="Text of the TODO to reopen.")


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

DEPENDENCY_PROMPT = """You are a helpful assistant that helps a user with their tasks and todos. The user can add a todos, mark todos as completed, or reopen certain todos.
The user can provide multiple actions at once so you've to break those down and call the appropriate functions in the correct sequence."""

user_messages = [{
    "role":
    "user",
    "content":
    """I have to pick up my daughter from school. After which I've to do the laundary. And now I need to cook lunch."""
}]

print("*" * 100)
print("SYNC")

output = tool("claude-3-sonnet-20240229",
              user_messages,
              functions,
              None,
              True,
              DEPENDENCY_PROMPT,
              max_tokens=3000)

if output:
    print(json.dumps(output, indent=4))
else:
    print("Unable to find a function!")
print("*" * 100)

tool = AsyncTool(ANTHROPIC_API_KEY)

print("*" * 100)
print("ASYNC")
output = asyncio.run(
    tool("claude-3-sonnet-20240229",
         user_messages,
         functions,
         None,
         True,
         DEPENDENCY_PROMPT,
         max_tokens=3000))
if output:
    print(json.dumps(output, indent=4))
else:
    print("Unable to find a function!")
print("*" * 100)
