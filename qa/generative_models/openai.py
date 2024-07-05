from openai import OpenAI
import os

def get_response(system_prompt, messages, model_id, temp=0.0, max_tok=1000):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    messages = [{"role": "system", "content": system_prompt}] + messages

    kwargs = {
        "model": model_id,
        "max_tokens": max_tok,
        "temperature": temp,
        "messages": messages
    }

    message = client.chat.completions.create(**kwargs)
    return message.choices[0].message.content
