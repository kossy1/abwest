"""
URL configuration for the adaptive learning platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API routes
    path('api/', include('api.urls')),
    path('api/auth/', include('rest_framework.urls')),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Apps
    path('core/', include('core.urls')),
    path('ml-models/', include('ml_models.urls')),
    path('learning-paths/', include('learning_paths.urls')),
    path('knowledge-graph/', include('knowledge_graph.urls')),
    path('data-ingestion/', include('data_ingestion.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)