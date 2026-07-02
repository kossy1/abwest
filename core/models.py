# core/models.py - PyMongo Models (No Django ORM)
from django.db import models
from datetime import datetime
import json

# These are helper classes for MongoDB documents
# They don't create Django database tables

class MongoModel:
    """Base class for MongoDB documents"""
    
    @classmethod
    def get_collection(cls):
        """Get MongoDB collection for this model"""
        from project_config.settings import mongodb_db
        return mongodb_db[cls._collection_name]
    
    @classmethod
    def find(cls, filter=None):
        """Find documents in collection"""
        if filter is None:
            filter = {}
        return cls.get_collection().find(filter)
    
    @classmethod
    def find_one(cls, filter=None):
        """Find one document"""
        if filter is None:
            filter = {}
        return cls.get_collection().find_one(filter)
    
    @classmethod
    def insert_one(cls, data):
        """Insert one document"""
        return cls.get_collection().insert_one(data)
    
    @classmethod
    def update_one(cls, filter, update):
        """Update one document"""
        return cls.get_collection().update_one(filter, update)
    
    @classmethod
    def delete_one(cls, filter):
        """Delete one document"""
        return cls.get_collection().delete_one(filter)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class Course(MongoModel):
    _collection_name = 'courses'
    
    def __init__(self, data=None):
        if data:
            for key, value in data.items():
                setattr(self, key, value)
    
    @classmethod
    def create(cls, title, description=None, difficulty='beginner', topics=None, instructor=None):
        """Create a new course"""
        data = {
            'title': title,
            'description': description,
            'difficulty_level': difficulty,
            'topics': topics or [],
            'instructor': instructor,
            'created_at': datetime.now().isoformat(),
            'published': False
        }
        result = cls.insert_one(data)
        return cls.find_one({'_id': result.inserted_id})

class Question(MongoModel):
    _collection_name = 'questions'
    
    def __init__(self, data=None):
        if data:
            for key, value in data.items():
                setattr(self, key, value)
    
    @classmethod
    def create(cls, course_id, topic, difficulty, question_text, options, correct_answer, explanation=None):
        """Create a new question"""
        data = {
            'course_id': course_id,
            'topic': topic,
            'difficulty': difficulty,
            'question_text': question_text,
            'options': options,
            'correct_answer': correct_answer,
            'explanation': explanation,
            'created_at': datetime.now().isoformat(),
            'times_used': 0,
            'times_correct': 0
        }
        result = cls.insert_one(data)
        return cls.find_one({'_id': result.inserted_id})

class QuizAttempt(MongoModel):
    _collection_name = 'quiz_attempts'
    
    @classmethod
    def create(cls, user_id, course_id):
        """Start a new quiz attempt"""
        data = {
            'user_id': user_id,
            'course_id': course_id,
            'current_ability': 0.5,
            'questions_answered': [],
            'start_time': datetime.now().isoformat(),
            'completed': False,
            'final_score': None
        }
        result = cls.insert_one(data)
        return cls.find_one({'_id': result.inserted_id})