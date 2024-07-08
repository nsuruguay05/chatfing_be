from rest_framework import serializers

from qa.models import Question, Answer, Evaluation, AnswerMethod
from documents.serializers import ChunkSerializer

class AnswerSerializer(serializers.ModelSerializer):
    answer = serializers.SerializerMethodField()
    references = ChunkSerializer(many=True, read_only=True)

    class Meta:
        model = Answer
        fields = ['id', 'answer', 'references', 'derivation', 'generative_model', 'method', 'temperature', 'created_at', 'updated_at']
    
    def _get_leafs_derivation(self, derivation):
        if 'children' in derivation and derivation['children']:
            leafs = []
            for child in derivation['children']:
                leafs += self._get_leafs_derivation(child)
            return list(set(leafs))
        return [derivation['text']]

    def get_answer(self, answer):
        answer_msg = answer.answer
        if answer.method == AnswerMethod.DERIVATION.value and isinstance(answer.derivation, dict):
            used_refs = ['\n- ' + ref for ref in self._get_leafs_derivation(answer.derivation)]
            answer_msg += f"\n\n**Referencias:**{''.join(used_refs)}"
        return answer_msg

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