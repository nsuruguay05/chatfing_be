from rest_framework import serializers

from qa.models import Question, Answer, Evaluation
from documents.serializers import ChunkSerializer

class AnswerSerializer(serializers.ModelSerializer):
    references = ChunkSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'answer', 'references', 'derivation', 'generative_model', 'method', 'temperature', 'created_at', 'updated_at']

class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'question', 'answers', 'created_at', 'updated_at']
    
    def get_answers(self, question):
        answers = question.answer_set.all()
        return AnswerSerializer(answers, many=True).data

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'