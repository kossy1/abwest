# settings.py
import os
import mongoengine
from dotenv import load_dotenv

load_dotenv()

# ============================
# MONGODB CONFIGURATION
# ============================
MONGODB_URI = os.environ.get('MONGODB_URI')
MONGODB_DB_NAME = os.environ.get('MONGODB_DB_NAME', 'adaptive_learning')

# Connect to MongoDB using MongoEngine
mongoengine.connect(
    db=MONGODB_DB_NAME,
    host=MONGODB_URI,
    alias='default'
)

# If using PyMongo directly (for raw queries)
import pymongo
mongodb_client = pymongo.MongoClient(MONGODB_URI)
mongodb_db = mongodb_client[MONGODB_DB_NAME]

# ============================
# DJANGO DATABASES (Optional)
# ============================
# Keep Django's default SQLite or PostgreSQL for auth/sessions
# Use MongoDB for course content, questions, and analytics
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    # Uncomment if using PostgreSQL for user management
    # 'users': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'adaptive_users',
    #     'USER': 'postgres',
    #     'PASSWORD': 'password',
    #     'HOST': 'localhost',
    #     'PORT': '5432',
    # }
}

# ============================
# DATABASE ROUTER (Optional)
# ============================
# If using multiple databases, route models to appropriate DB
class MongoRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ['core', 'ml_models']:
            return 'default'  # SQLite for Django admin
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['core', 'ml_models']:
            return 'default'
        return None

# Uncomment to enable:
# DATABASE_ROUTERS = ['your_project.settings.MongoRouter']

# ============================
# INSTALLED APPS
# ============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'corsheaders',
    'storages',
    'ckeditor',
    'import_export',
    
    # Your apps
    'api',
    'core',
    'ml_models',
    'learning_paths',
    'knowledge_graph',
    'data_ingestion',
]