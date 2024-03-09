import asyncio
from configs import ANTHROPIC_API_KEY
from pydantic import BaseModel, Field
from typing import List, Dict
import json
from claudetools.tools.tool import Tool, AsyncTool

tool = Tool(ANTHROPIC_API_KEY)


class QueryDependency(BaseModel):
    id: int = Field(..., description="Unique Integer Id for the Query")
    question: str = Field(
        ...,
        description=
        "Question we want to ask to get a better context or more background about the main question.",
    )


class Dependencies(BaseModel):
    dependencies: List[QueryDependency] = Field(
        ...,
        description=
        "A list of query dependencies in the correct sequence to fetch more background information about the main question.",
    )


functions = [{
    "name": "dependencyPlanning",
    "description":
    "Plan a sequential list of all the sub-questions that once answered can provide more background to answer the main question.",
    "parameters": Dependencies.model_json_schema()
}]

DEPENDENCY_SYSTEM_PROMPT = """You're a query planning agent. Given a user message provide all the question or context dependencies that would need to be addressed to provide a response to the user.
You've to break down questions into its dependent queries such that the answers of the dependent query can be used to inform the parent question.
You don't need to answer the questions, simply provide the correct sequence of questions to ask and relevant dependencies.
Call the function with appropriate data i.e. the dependencies.
"""

question = "what's the distance between the capital of France and capital of UK?"
user_messages = [{"role": "user", "content": question}]

print("*" * 100)
print("SYNC")
output = tool("claude-3-sonnet-20240229",
              user_messages,
              functions,
              None,
              False,
              DEPENDENCY_SYSTEM_PROMPT,
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
         False,
         DEPENDENCY_SYSTEM_PROMPT,
         max_tokens=3000))
if output:
    print(json.dumps(output, indent=4))
else:
    print("Unable to find a function!")
print("*" * 100)
