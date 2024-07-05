from documents.retrieval_methods.knn_retrieval import retrieve
from documents.retrieval_models.routing import EmbeddingModel
from qa.generative_models.routing import GET_RESPONSE

# Función para generar prompt
def create_answer(message, model, temperature=0):
    """
    Create the answer for the user message using a naive RAG approach.

    Parameters:
    - message: String, the user message
    - model: String, the model to use for generating the response

    Returns:
    - response: String, the response to the user message
    - references: List of Chunk, the references used to generate the response
    """
    references = retrieve(EmbeddingModel.OPENAI_3_SMALL.value, message)

    system_msg = f'''Mantener una conversación sobre extractos de documentos relacionados con la Facultad de Ingeniería de la Universidad de la República de Uruguay. Dar respuestas cortas, concretas y precisas. Utilizar únicamente la información de los siguientes extractos para construir la respuesta:

{references[0].chunk.strip()}

{references[1].chunk.strip()}

{references[2].chunk.strip()}

---

Si los extractos no tienen una relación evidente con la pregunta, ignorarlos y responder que no se cuenta con información para responder la pregunta. Evitar las suposiciones. La conversación debe ser en español. Recuerda ser concreto.

Mencionar a los extractos es incorrecto ya que el usuario no sabe lo que son. En cambio, puedes mencionar las fuentes (los documentos de donde surgen los extractos).

Siempre agregar al final de la respuesta los links a las referencias que se utilizaron en la respuesta bajo el título de "**Referencias:**".

IMPORTANTE: Responder en español.'''

    messages = [{"role": "user", "content": message}]

    return GET_RESPONSE[model](system_msg, messages, model, temp=temperature), references