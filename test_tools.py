from ai_core.llm_client import LLMClient
from ai_core.tool_schemas import TOOLS


client = LLMClient()

messages = [
    {
        "role": "system",
        "content": """
You are Aegis, a local Windows AI assistant.

You understand natural language and select appropriate tools.

You must only use the tools provided to you.
Do not generate PowerShell or shell commands.
Do not execute anything yourself.
"""
    },
    {
        "role": "user",
        "content": "Tell me a joke"
    }
]


response = client.chat(
    messages=messages,
    tools=TOOLS
)

print("CONTENT:")
print(response.message.content)

print("\nTOOL CALLS:")
print(response.message.tool_calls)