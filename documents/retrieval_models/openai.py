from openai import OpenAI
import os

def create_embeddings(model_id, texts):
    """
    Create embeddings using a specific model id from OpenAI for a list of texts.
    
    Parameters:
    - model_id: str, the model to use
    - texts: list of strings, the texts to create embeddings for
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        res = client.embeddings.create(input=texts, model=model_id)
        return [d.embedding for d in res.data]
    except Exception as e:
        print(f"Error creating embeddings: {e}")
        raise Exception(f"Error creating embeddings: {e}") from e