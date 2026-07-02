# project_config/wsgi.py
import os
import sys

# Add project root to Python path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()