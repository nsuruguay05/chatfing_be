from sklearn.neighbors import NearestNeighbors

from documents.models import Embedding
from documents.retrieval_models.routing import CREATE_EMBEDDINGS

def retrieve(model_emb, message, k=3):
    """
    Retrieve the most similar chunks to a message.

    Parameters:
    - model_emb: String, the embedding model to use
    - message: String, the message to retrieve the most similar chunks for
    - k: Int, the number of chunks to retrieve

    Returns:
    - references: List of Chunk, the most similar chunks to the message
    """
    embeddings_objs = Embedding.objects.filter(model=model_emb, chunk__document__active=True)
    embeddings = [e.embedding for e in embeddings_objs]
    
    model_knn = NearestNeighbors(n_neighbors=k)
    model_knn.fit(embeddings)

    references_ids = model_knn.kneighbors(CREATE_EMBEDDINGS[model_emb](model_emb, [message]))[1][0]
    references = [embeddings_objs[int(i)].chunk for i in references_ids]

    return references