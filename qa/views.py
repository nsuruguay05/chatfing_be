from rest_framework import generics, status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response

from qa.generation_methods import naive_rag, derivation, long_context
from qa.generative_models.routing import GenerativeModel
from qa.models import Question, Answer, Evaluation
from qa.serializers import QuestionSerializer, AnswerSerializer, EvaluationSerializer

class QuestionList(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class CreateAnswer(APIView):
    def get_object(self, pk):
        try:
            return Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        question = self.get_object(pk)

        # Get the generative model to use
        generative_model = request.data.get('generative_model')
        if generative_model not in [model.name for model in GenerativeModel]:
            return Response({'message': 'Invalid generative model'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the temperature (if any)
        temperature = request.data.get('temperature')
        if temperature is not None:
            try:
                temperature = float(temperature)
                if temperature < 0 or temperature > 1:
                    return Response({'message': 'Invalid temperature: must be between 0 and 1'}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError:
                return Response({'message': 'Invalid temperature: must be a float number'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            temperature = 0

        # Get the method to use
        try:
            method = request.data.get('method')
            steps = None
            if method == 'naive_rag':
                answer, references = naive_rag.create_answer(question.question, GenerativeModel[generative_model].value, temperature)
            elif method == 'derivation':
                answer, references, steps = derivation.create_answer(question.question, GenerativeModel[generative_model].value, temperature)
            elif method == 'long_context':
                answer, references = long_context.create_answer(question.question, GenerativeModel[generative_model].value, temperature)
            else:
                return Response({'message': 'Invalid method'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'message': 'Error generating answer'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Create the answer object and the references
        obj = Answer.objects.create(
            question=question,
            answer=answer,
            derivation=steps,
            generative_model=GenerativeModel[generative_model].value,
            method=method,
            temperature=temperature
        )
        obj.references.set(references)

        serializer = AnswerSerializer(obj)
        return Response(serializer.data)

class QuestionDetail(generics.RetrieveDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class EvaluateAnswer(APIView):
    def get_object(self, pk):
        try:
            return Answer.objects.get(pk=pk)
        except Answer.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        answer = self.get_object(pk)

        like = request.data.get('like')
        comment = request.data.get('comment')
        evaluation_author = request.data.get('evaluation_author')
        
        if like is None and comment is None:
            return Response({'message': 'Invalid evaluation'}, status=status.HTTP_400_BAD_REQUEST)
        
        eval = Evaluation.objects.create(
            answer=answer,
            like=like,
            comment=comment,
            author=evaluation_author
        )
        serializer = EvaluationSerializer(eval)
        return Response(serializer.data)