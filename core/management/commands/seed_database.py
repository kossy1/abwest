
"""
Custom management command to seed MongoDB with test data.
Run: python manage.py seed_database
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Course, Question
from mongoengine import connect
import json
import random
from datetime import datetime

class Command(BaseCommand):
    help = 'Seed the database with test data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sample-size',
            type=int,
            default=100,
            help='Number of sample questions to generate'
        )

    def handle(self, *args, **options):
        sample_size = options['sample_size']
        self.stdout.write(f'Seeding database with {sample_size} questions...')
        
        # Check if MongoDB is connected
        try:
            from core.models import Course
            Course.objects.count()
        except Exception as e:
            self.stderr.write(f'MongoDB connection error: {e}')
            self.stderr.write('Make sure MongoDB is running and MONGODB_URI is set')
            return
        
        # Sample course data
        courses = [
            {
                'title': 'Introduction to Python Programming',
                'description': 'Learn Python from scratch with hands-on projects',
                'difficulty_level': 'beginner',
                'topics': ['python', 'programming', 'basics', 'functions']
            },
            {
                'title': 'Machine Learning Fundamentals',
                'description': 'Understand core ML concepts and algorithms',
                'difficulty_level': 'intermediate',
                'topics': ['machine learning', 'data science', 'algorithms']
            },
            {
                'title': 'Advanced Deep Learning',
                'description': 'Deep dive into neural networks and architectures',
                'difficulty_level': 'advanced',
                'topics': ['deep learning', 'neural networks', 'CNNs', 'RNNs']
            },
        ]
        
        # Create courses if they don't exist
        created_courses = []
        for course_data in courses:
            course, created = Course.objects.get_or_create(
                title=course_data['title'],
                defaults={
                    'description': course_data['description'],
                    'difficulty_level': course_data['difficulty_level'],
                    'topics': course_data['topics']
                }
            )
            created_courses.append(course)
            if created:
                self.stdout.write(f'✓ Created course: {course.title}')
        
        # Generate sample questions
        topics = ['python', 'programming', 'functions', 'loops', 'classes',
                  'machine learning', 'data science', 'statistics', 'algorithms',
                  'deep learning', 'neural networks', 'CNNs', 'RNNs']
        
        question_templates = [
            {
                'question': 'What is the output of the following code?',
                'options': ['A) 10', 'B) 20', 'C) 30', 'D) Error'],
                'correct_answer': 'B) 20'
            },
            {
                'question': 'Which of the following is a supervised learning algorithm?',
                'options': ['A) K-Means', 'B) Linear Regression', 'C) PCA', 'D) Apriori'],
                'correct_answer': 'B) Linear Regression'
            },
            # Add more templates as needed
        ]
        
        questions_created = 0
        for i in range(sample_size):
            course = random.choice(created_courses)
            topic = random.choice(topics)
            difficulty = random.uniform(0.1, 0.9)
            template = random.choice(question_templates)
            
            question = Question(
                course=course,
                topic=topic,
                difficulty=difficulty,
                question_text=template['question'],
                options=template['options'],
                correct_answer=template['correct_answer'],
                explanation=f'This is an auto-generated explanation for question {i+1}',
                tags=[topic, course.difficulty_level]
            )
            question.save()
            questions_created += 1
            
            if questions_created % 10 == 0:
                self.stdout.write(f'✓ Created {questions_created} questions...')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ Successfully seeded database with:'
                f'\n  - {len(created_courses)} courses'
                f'\n  - {questions_created} questions'
            )
        )