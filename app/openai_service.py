from typing import Dict, List
from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import Glossary

load_dotenv()

def format_glossary_item(item: Glossary):
    return f"({item.term}) | ({item.translation}) |" + (f" ({item.comment})" if item.comment else "")

class Assistant:
    def __init__(self, model: str, policy: str, temperature: float):
        self._client = OpenAI()
        self._model = model
        self._policy = policy
        self._temperature = temperature

    def __call__(self, messages: List[Dict[str, str]], glossary_list: list[Glossary]):
    
        system_promt = self._policy + "\nГлоссарий:\n" + "\n".join([format_glossary_item(glossary_item) for glossary_item in glossary_list]) + '\n'

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{ "role": "system", "content": system_promt }] + messages,
            temperature=self._temperature
        )
        return response.choices[0].message.content