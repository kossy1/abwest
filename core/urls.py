# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Public
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # User Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Student - Courses
    path('courses/', views.student_courses, name='student_courses'),
    path('courses/<int:course_id>/', views.student_course_detail, name='student_course_detail'),
    
    # Student - Quizzes
    path('quizzes/', views.student_quizzes, name='student_quizzes'),
    path('quizzes/take/<int:quiz_id>/', views.student_take_quiz, name='student_take_quiz'),
    path('quizzes/result/<int:quiz_id>/', views.student_quiz_result, name='student_quiz_result'),
    
    # Student - Progress
    path('progress/', views.student_progress, name='student_progress'),
    
    # Admin Dashboard
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Admin - Students
    path('admin/students/', views.admin_students, name='admin_students'),
    path('admin/students/<int:student_id>/', views.admin_student_detail, name='admin_student_detail'),
    path('admin/students/<int:student_id>/edit/', views.admin_student_edit, name='admin_student_edit'),
    path('admin/students/<int:student_id>/delete/', views.admin_student_delete, name='admin_student_delete'),
    path('admin/students/<int:student_id>/toggle/', views.admin_student_toggle, name='admin_student_toggle'),
    
    # Admin - Courses
    path('admin/courses/', views.admin_courses, name='admin_courses'),
    path('admin/courses/create/', views.admin_course_create, name='admin_course_create'),
    path('admin/courses/<int:course_id>/edit/', views.admin_course_edit, name='admin_course_edit'),
    path('admin/courses/<int:course_id>/delete/', views.admin_course_delete, name='admin_course_delete'),
    
    # Admin - Quizzes
    path('admin/quizzes/', views.admin_quizzes, name='admin_quizzes'),
    path('admin/quizzes/create/', views.admin_quiz_create, name='admin_quiz_create'),
    path('admin/quizzes/<int:quiz_id>/edit/', views.admin_quiz_edit, name='admin_quiz_edit'),
    path('admin/quizzes/<int:quiz_id>/delete/', views.admin_quiz_delete, name='admin_quiz_delete'),
    path('admin/quizzes/<int:quiz_id>/questions/', views.admin_quiz_questions, name='admin_quiz_questions'),
    
    # Admin - Analytics
    path('admin/analytics/', views.admin_analytics, name='admin_analytics'),
    
    # API
    path('api/analytics-data/', views.api_analytics_data, name='api_analytics_data'),
    path('api/stats/', views.api_stats, name='api_stats'),
]