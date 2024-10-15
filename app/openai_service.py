from dotenv import load_dotenv
from openai import OpenAI

from app.schemas import Glossary

load_dotenv()
client = OpenAI()

def format_glossary_item(item: Glossary):
    return f"({item.term}) | ({item.translation}) |" + (f" ({item.comment})" if item.comment else "")

def generate_response(messages, policy, glossary_list: list[Glossary]):
    
    system_promt = policy + "\nГлоссарий:\n" + "\n".join([format_glossary_item(glossary_item) for glossary_item in glossary_list]) + '\n'

    print(system_promt)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{ "role": "system", "content": system_promt }] + messages,
        temperature=0.2
    )
    return response.choices[0].message.content