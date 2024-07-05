from anthropic import Anthropic
import os

def get_response(system_prompt, messages, model_id, temp=0.0, max_tok=1000):
    client = Anthropic(
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    kwargs = {
        "model": model_id,
        "max_tokens": max_tok,
        "temperature": temp,
        "system": system_prompt,
        "messages": messages
    }

    if kwargs["system"] is None:
        del kwargs["system"]

    message = client.messages.create(**kwargs)
    return message.content[0].text
