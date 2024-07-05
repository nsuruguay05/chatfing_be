from django.urls import path
from qa import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('questions/', views.QuestionList.as_view()),
    path('questions/<int:pk>/', views.QuestionDetail.as_view()),
    path('questions/<int:pk>/create_answer/', views.CreateAnswer.as_view()),
    path('answers/<int:pk>/evaluate/', views.EvaluateAnswer.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)