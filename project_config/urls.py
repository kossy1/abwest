# project_config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

# Simple health check view (fallback)
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Adaptive Learning Platform is running!'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # <-- This includes all core app URLs
    path('health/', health_check, name='health'),
]