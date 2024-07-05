from django.db import models
from django.contrib.postgres.fields import ArrayField
import pandas as pd

from documents.retrieval_models.routing import EmbeddingModel, CREATE_EMBEDDINGS

class Document(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField(null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'document'

    def __str__(self):
        return self.title
    
    @staticmethod
    def load_chunks_documents(csv_path):
        """
        Load documents from a CSV file.
        
        The CSV file must have the chunks of the documents. The columns must be:
        - title: str, the title of the document
        - source: str, the URL of the document
        - chunk: str, the text of the chunk

        Chunks should be ordered by their position in the document.
        
        Parameters:
        - csv_path: str, path to the CSV file
        """
        chunks = pd.read_csv(csv_path)

        # Create documents
        documents = {}
        for title, source in chunks[['title', 'source']].values:
            if title not in documents:
                document = Document.objects.create(title=title, url=source)
                documents[title] = {'document': document, 'current_position': 0}

        # Create chunks
        chunks_objs = []
        for title, source, chunk in chunks[['title', 'source', 'chunk']].values:
            document = documents[title]['document']
            current_position = documents[title]['current_position']
            chunk_with_header = f"Extracto de página web de título: {title} - URL: {source}\n{chunk}"
            new_chunk = Chunk.objects.create(document=document, chunk=chunk_with_header, position=current_position)
            documents[title]['current_position'] += 1
            chunks_objs.append(new_chunk)
        
        return chunks_objs

class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    chunk = models.TextField()
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        db_table = 'chunk'

    def __str__(self):
        return "Chunk {} of document {}".format(self.position, self.document.title)

class Embedding(models.Model):
    chunk = models.ForeignKey(Chunk, on_delete=models.CASCADE)
    model = models.CharField(max_length=50, choices=EmbeddingModel.choices(), default=EmbeddingModel.OPENAI_3_SMALL.value)
    embedding = ArrayField(models.FloatField())
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'embedding'

    def __str__(self):
        return "Embedding for chunk {} with model {}".format(self.chunk, self.model)
    
    @staticmethod
    def create_embeddings(model, chunks):
        """
        Create embeddings using a specific model for a list of chunks.
        
        Parameters:
        - model: str, the model to use
        - chunks: list of Chunk, the chunks to create embeddings for
        """
        texts = [chunk.chunk for chunk in chunks]
        if model not in CREATE_EMBEDDINGS:
            raise ValueError(f"Model {model} not supported")
        embeddings = CREATE_EMBEDDINGS[model](model, texts)
        for i, chunk in enumerate(chunks):
            Embedding.objects.create(chunk=chunk, model=model, embedding=embeddings[i])
