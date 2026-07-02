# api/urls.py
from django.urls import path
from core.views import home, get_courses, get_questions, start_quiz

urlpatterns = [
    path('', home, name='home'),
    path('courses/', get_courses, name='courses'),
    path('questions/<str:course_id>/', get_questions, name='questions'),
    path('quiz/start/', start_quiz, name='start_quiz'),
]