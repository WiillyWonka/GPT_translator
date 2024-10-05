from dotenv import load_dotenv
import openai

load_dotenv()

def generate_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message['content'].strip()