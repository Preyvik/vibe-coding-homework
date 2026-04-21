import os
import json
import math
from pprint import pprint
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)


def calculate(expression: str):
    """Safely evaluate a simple arithmetic expression."""
    allowed_chars = set("0123456789+-*/().% ")
    allowed_names = {"sqrt": math.sqrt, "pi": math.pi, "e": math.e}

    if not all(c in allowed_chars or c.isalpha() for c in expression):
        return {"error": "expression contains disallowed characters"}

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
    except Exception as exc:
        return {"error": str(exc)}

    return {"expression": expression, "result": result}


tools = [
    {
        "name": "calculate",
        "description": (
            "Evaluate a Python arithmetic expression. "
            "Supports +, -, *, /, %, parentheses, sqrt(), pi, e."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Arithmetic expression, e.g. '127 * 349 + 2024'",
                }
            },
            "required": ["expression"],
        },
    },
]

available_functions = {
    "calculate": calculate,
}


def get_completion_from_messages(messages, model="claude-sonnet-4-5"):
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system="You are a helpful AI assistant. Use the calculate tool for arithmetic.",
        messages=messages,
        tools=tools,
        tool_choice={"type": "auto"}
    )

    print("First response:", response)

    has_tool_call = any(item.type == "tool_use" for item in response.content)

    if has_tool_call:
        tool_call = next(item for item in response.content if item.type == "tool_use")

        function_name = tool_call.name
        function_args = tool_call.input
        tool_id = tool_call.id

        function_to_call = available_functions[function_name]
        function_response = function_to_call(**function_args)

        messages.append({
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": tool_id,
                    "name": function_name,
                    "input": function_args
                }
            ]
        })

        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_id,
                    "content": json.dumps(function_response)
                }
            ]
        })

        second_response = client.messages.create(
            model=model,
            max_tokens=1024,
            system="You are a helpful AI assistant. Use the calculate tool for arithmetic.",
            messages=messages,
        )

        return second_response

    return response


messages = [
    {"role": "user", "content": "What is 127 * 349 + 2024?"},
]

response = get_completion_from_messages(messages)
print("--- Full response: ---")
pprint(response)
print("--- Response text: ---")
if response.content and hasattr(response.content[0], 'text'):
    print(response.content[0].text)
else:
    print("No text content in the response")
