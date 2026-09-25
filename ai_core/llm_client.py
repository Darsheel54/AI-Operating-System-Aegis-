from ollama import Client
from config import OLLAMA_HOST, MODEL_NAME


class LLMClient:

    def __init__(self):
        self.client = Client(host=OLLAMA_HOST)
        self.model = MODEL_NAME

    def chat(self, messages, tools=None):

        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools
        )

        return response