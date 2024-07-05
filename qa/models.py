from django.db import models
from enum import Enum

from documents.models import Chunk
from qa.generative_models.routing import GenerativeModel

class AnswerMethod(Enum):
    NAIVE_RAG = 'naive_rag'
    DERIVATION = 'derivation'
    LONG_CONTEXT = 'long_context'

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class Question(models.Model):
    question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        ordering = ['-created_at']
        db_table = 'question'

    def __str__(self):
        return self.question

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField()
    references = models.ManyToManyField(Chunk, db_table='answer_reference')
    derivation = models.JSONField(null=True)
    generative_model = models.CharField(max_length=50, choices=GenerativeModel.choices(), default=GenerativeModel.CLAUDE_3_HAIKU.value)
    method = models.CharField(max_length=20, choices=AnswerMethod.choices(), default=AnswerMethod.NAIVE_RAG.value)
    temperature = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        db_table = 'answer'

    def __str__(self):
        return self.answer

class Evaluation(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='evaluations')
    like = models.BooleanField(null=True)
    comment = models.TextField(null=True)
    author = models.TextField(null=True, default="Anónimo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class meta:
        db_table = 'evaluation'

    def __str__(self):
        return self.comment