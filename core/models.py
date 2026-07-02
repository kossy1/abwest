# core/models.py (MongoEngine version)
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

class User(Document):
    username = fields.StringField(max_length=150, unique=True, required=True)
    email = fields.EmailField(unique=True, required=True)
    password_hash = fields.StringField(required=True)
    full_name = fields.StringField(max_length=200)
    role = fields.StringField(choices=['student', 'instructor', 'admin'], default='student')
    enrolled_courses = fields.ListField(fields.ReferenceField('Course'))
    learning_style = fields.StringField(choices=['visual', 'auditory', 'kinesthetic'])
    created_at = fields.DateTimeField(default=datetime.now)
    last_active = fields.DateTimeField(default=datetime.now)
    
    meta = {'collection': 'users'}

class Course(Document):
    title = fields.StringField(max_length=200, required=True)
    description = fields.StringField()
    instructor = fields.ReferenceField('User')
    difficulty_level = fields.StringField(choices=['beginner', 'intermediate', 'advanced'])
    topics = fields.ListField(fields.StringField())
    prerequisites = fields.ListField(fields.ReferenceField('self'))
    estimated_duration = fields.IntField()  # in hours
    created_at = fields.DateTimeField(default=datetime.now)
    published = fields.BooleanField(default=False)
    
    meta = {'collection': 'courses'}

class Question(Document):
    course = fields.ReferenceField('Course', required=True)
    topic = fields.StringField(required=True)
    difficulty = fields.FloatField(min_value=0, max_value=1, required=True)
    question_text = fields.StringField(required=True)
    options = fields.ListField(fields.StringField(), required=True)
    correct_answer = fields.StringField(required=True)
    explanation = fields.StringField()
    tags = fields.ListField(fields.StringField())
    created_at = fields.DateTimeField(default=datetime.now)
    times_used = fields.IntField(default=0)
    times_correct = fields.IntField(default=0)
    
    meta = {'collection': 'questions'}

class QuizAttempt(Document):
    user = fields.ReferenceField('User', required=True)
    course = fields.ReferenceField('Course', required=True)
    current_ability = fields.FloatField(default=0.5)
    questions_answered = fields.ListField(fields.DictField())
    start_time = fields.DateTimeField(default=datetime.now)
    end_time = fields.DateTimeField()
    completed = fields.BooleanField(default=False)
    final_score = fields.FloatField()
    
    meta = {'collection': 'quiz_attempts'}

class Progress(Document):
    user = fields.ReferenceField('User', required=True)
    course = fields.ReferenceField('Course', required=True)
    modules_completed = fields.ListField(fields.StringField())
    quiz_scores = fields.ListField(fields.FloatField())
    average_score = fields.FloatField(default=0)
    time_spent = fields.IntField(default=0)  # in minutes
    last_activity = fields.DateTimeField(default=datetime.now)
    current_streak = fields.IntField(default=0)
    
    meta = {'collection': 'progress'}