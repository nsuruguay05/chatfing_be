from enum import Enum
from documents.retrieval_models.openai import create_embeddings as create_embeddings_openai

class EmbeddingModel(Enum):
    OPENAI_3_SMALL = 'text-embedding-3-small'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

CREATE_EMBEDDINGS = {
    EmbeddingModel.OPENAI_3_SMALL.value: create_embeddings_openai
}