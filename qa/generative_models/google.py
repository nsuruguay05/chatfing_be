import google.generativeai as genai
import os

ROLES_MAP = {
    "assistant": "model",
    "user": "user",
}

def get_response(system_prompt, messages, model_id, temp=0.0, max_tok=1000):
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

    generation_config = {
        "temperature": temp,
        "max_output_tokens": max_tok,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name=model_id,
        generation_config=generation_config,
        system_instruction=system_prompt,
    )

    history = [{"role": ROLES_MAP[m["role"]], "parts": [m["content"]]} for m in messages[:-1]]

    chat_session = model.start_chat(history=history)

    response = chat_session.send_message(messages[-1]["content"])
    return response.text