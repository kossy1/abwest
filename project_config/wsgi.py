import os
import sys
import django

# Add the project root to Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')

# Initialize Django
django.setup()

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()