# project_config/urls.py
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Adaptive Learning Platform is running!',
        'environment': 'development'
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', health_check, name='home'),
    path('health/', health_check, name='health'),
]