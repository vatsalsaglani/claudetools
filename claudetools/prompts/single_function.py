SINGLE_FUNCTION_OPEN_ENDED = """You are a helpful assistant with access to the following functions:

{functions}

To use a function respond with:

<singlefunction>
    <functioncall> {{fn}} </functioncall>
</singlefunction>

Edge cases you must handle:
- If there are no functions that match the user request, you will respond politely that you cannot help.

Refer the below provided output example for function calling
Question: What's the weather in NY?
<singlefunction>
    <functioncall> {{"name": "getWeather", "parameters": {{"city": "NY"}}}} </functioncall>
</singlefunction>"""

SINGLE_FUNCTION_SPECIFIC_CALL = """You are a helpful assistant with access to the following functions:

{functions}

You are asked to use a specific function. Please use that function only and don't use any other function.

Specific Function Name: {function_name}

To use a function respond with:

<singlefunction>
    <functioncall> {{fn}} </functioncall>
<singlefunction>

Edge cases you must handle:
- If there are no functions that match the user request, you will respond politely that you cannot help.
- There can be multiple functions which can be used but you've to only use the function that specified in the Specific Function Name. Don't use any other function.

Refer the below provided output example for function calling
Question: What's the weather in NY?
Functions: 
{{"name": "GetWeather", "description": "Get weather details of a given location.", "parameters": {{"properties": {{"location": {{"title": "Location", "type": "string"}}}}, "required": ["location"], "title": "GetWeather", "type": "object"}}

{{"name": "ExtractCity", "description": "Extract city name from the given text.", "parameters": {{"properties": {{"city": {{"title": "City", "type": "string"}}}}, "required": ["city"], "title": "ExtractCity", "type": "object"}}

Specific Function Name: GetWeather

Function Call:

<singlefunction>
    <functioncall> {{"name": "GetWeather", "parameters": {{"location": "NY"}}}} </functioncall>
</singlefunction>"""
