from django.contrib import admin
from django.urls import path, include
from api.health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('health/', health_check, name='health_check'),
    path('', health_check, name='home'),  # Root goes to health check
]