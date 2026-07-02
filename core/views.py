# core/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Course, Question, QuizAttempt
from datetime import datetime
import random

def home(request):
    """Home page view"""
    return JsonResponse({
        'message': 'Welcome to Adaptive Learning Platform',
        'status': 'API is running'
    })

def get_courses(request):
    """Get all courses"""
    try:
        courses = list(Course.find())
        # Convert ObjectId to string for JSON
        for course in courses:
            course['_id'] = str(course['_id'])
        return JsonResponse({'courses': courses}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_questions(request, course_id):
    """Get questions for a course"""
    try:
        questions = list(Question.find({'course_id': course_id}))
        for q in questions:
            q['_id'] = str(q['_id'])
        return JsonResponse({'questions': questions}, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def start_quiz(request):
    """Start a new quiz"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        import json
        data = json.loads(request.body)
        user_id = data.get('user_id')
        course_id = data.get('course_id')
        
        if not user_id or not course_id:
            return JsonResponse({'error': 'user_id and course_id required'}, status=400)
        
        # Get questions for this course
        questions = list(Question.find({'course_id': course_id}))
        
        if not questions:
            return JsonResponse({'error': 'No questions found for this course'}, status=404)
        
        # Create quiz attempt
        attempt = QuizAttempt.create(user_id, course_id)
        
        # Select first question (medium difficulty)
        target_difficulty = 0.5
        selected_question = min(questions, key=lambda q: abs(q['difficulty'] - target_difficulty))
        selected_question['_id'] = str(selected_question['_id'])
        
        return JsonResponse({
            'attempt_id': str(attempt['_id']),
            'question': selected_question,
            'total_questions': len(questions)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)