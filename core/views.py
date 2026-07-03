# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime
import re
import json

# ============================================
# PUBLIC VIEWS
# ============================================

def index(request):
    """Landing page view"""
    return render(request, 'core/index.html')


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    return redirect('index')


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        role = request.POST.get('role', 'student')
        terms = request.POST.get('terms')
        
        errors = []
        
        if not fullname:
            errors.append('Full name is required.')
        if not username:
            errors.append('Username is required.')
        if not email:
            errors.append('Email address is required.')
        if not password:
            errors.append('Password is required.')
        if not confirm_password:
            errors.append('Please confirm your password.')
        if not terms:
            errors.append('You must agree to the terms and conditions.')
        
        if username and not re.match(r'^[a-zA-Z0-9_]{4,20}$', username):
            errors.append('Username must be 4-20 characters and contain only letters, numbers, and underscores.')
        
        if username and User.objects.filter(username=username).exists():
            errors.append('Username is already taken.')
        
        if email and not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            errors.append('Please enter a valid email address.')
        
        if email and User.objects.filter(email=email).exists():
            errors.append('Email address is already registered.')
        
        if password and len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        if password and not any(c.islower() for c in password):
            errors.append('Password must contain at least one lowercase letter.')
        if password and not any(c.isupper() for c in password):
            errors.append('Password must contain at least one uppercase letter.')
        if password and not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number.')
        
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'core/register.html', {
                'fullname': fullname,
                'username': username,
                'email': email,
                'role': role
            })
        
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.first_name = fullname.split()[0] if fullname else ''
            user.last_name = ' '.join(fullname.split()[1:]) if len(fullname.split()) > 1 else ''
            if role == 'instructor':
                user.is_staff = True
            user.save()
            
            login(request, user)
            messages.success(request, f'Welcome to EduAdapt, {user.username}!')
            
            if user.is_staff:
                return redirect('admin_dashboard')
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return render(request, 'core/register.html', {
                'fullname': fullname,
                'username': username,
                'email': email,
                'role': role
            })
    
    return render(request, 'core/register.html')


# ============================================
# USER DASHBOARD
# ============================================

@login_required
def dashboard(request):
    """User dashboard view with links to all student features"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Sample data - In production, fetch from database
    context = {
        'user': request.user,
        'enrolled_courses': 4,
        'completed_quizzes': 12,
        'average_score': 85,
        'current_streak': 7,
        'total_points': 2450,
        # Quick links
        'courses_url': 'student_courses',
        'quizzes_url': 'student_quizzes',
        'progress_url': 'student_progress',
    }
    return render(request, 'core/dashboard.html', context)


# ============================================
# STUDENT - COURSE VIEWS
# ============================================

@login_required
def student_courses(request):
    """View all courses a student is enrolled in"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Sample course data - In production, fetch from database
    enrolled_courses = [
        {
            'id': 1,
            'title': 'Python Programming',
            'description': 'Learn Python from scratch with hands-on projects and real-world applications.',
            'instructor': 'Dr. Smith',
            'progress': 85,
            'status': 'In Progress',
            'image': 'python',
            'level': 'Beginner',
            'modules': 12,
            'completed_modules': 10,
            'rating': 4.8,
            'last_accessed': datetime(2024, 1, 15),
            'upcoming_quiz': 'Python Basics Quiz'
        },
        {
            'id': 2,
            'title': 'Machine Learning Fundamentals',
            'description': 'Introduction to ML concepts, algorithms, and practical implementations.',
            'instructor': 'Prof. Johnson',
            'progress': 60,
            'status': 'In Progress',
            'image': 'ml',
            'level': 'Intermediate',
            'modules': 15,
            'completed_modules': 9,
            'rating': 4.9,
            'last_accessed': datetime(2024, 1, 20),
            'upcoming_quiz': 'ML Concepts Quiz'
        },
        {
            'id': 3,
            'title': 'Web Development with Django',
            'description': 'Build full-stack web applications using Django and modern frontend frameworks.',
            'instructor': 'Ms. Williams',
            'progress': 100,
            'status': 'Completed',
            'image': 'web',
            'level': 'Intermediate',
            'modules': 10,
            'completed_modules': 10,
            'rating': 4.7,
            'last_accessed': datetime(2024, 1, 10),
            'upcoming_quiz': None
        },
        {
            'id': 4,
            'title': 'Data Science & Analytics',
            'description': 'Data analysis, visualization, and business intelligence using Python.',
            'instructor': 'Dr. Chen',
            'progress': 30,
            'status': 'Not Started',
            'image': 'data',
            'level': 'Advanced',
            'modules': 14,
            'completed_modules': 4,
            'rating': 4.6,
            'last_accessed': None,
            'upcoming_quiz': 'Data Analysis Quiz'
        },
    ]
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        enrolled_courses = [c for c in enrolled_courses if c['status'].lower() == status_filter.lower()]
    
    context = {
        'courses': enrolled_courses,
        'total_courses': len(enrolled_courses),
        'in_progress': sum(1 for c in enrolled_courses if c['status'] == 'In Progress'),
        'completed': sum(1 for c in enrolled_courses if c['status'] == 'Completed'),
        'not_started': sum(1 for c in enrolled_courses if c['status'] == 'Not Started'),
        'status_filter': status_filter,
        'user': request.user,
    }
    return render(request, 'core/student_courses.html', context)


@login_required
def student_course_detail(request, course_id):
    """View details of a specific course"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Sample course detail - In production, fetch from database
    course = {
        'id': course_id,
        'title': 'Python Programming',
        'description': 'Learn Python from scratch with hands-on projects and real-world applications.',
        'instructor': 'Dr. Smith',
        'progress': 85,
        'status': 'In Progress',
        'level': 'Beginner',
        'modules': 12,
        'completed_modules': 10,
        'rating': 4.8,
        'enrolled_students': 45,
        'last_accessed': datetime(2024, 1, 15),
        'upcoming_quiz': 'Python Basics Quiz',
        'modules_list': [
            {'id': 1, 'title': 'Introduction to Python', 'completed': True, 'duration': '45 min'},
            {'id': 2, 'title': 'Variables and Data Types', 'completed': True, 'duration': '60 min'},
            {'id': 3, 'title': 'Control Flow', 'completed': True, 'duration': '50 min'},
            {'id': 4, 'title': 'Functions', 'completed': True, 'duration': '55 min'},
            {'id': 5, 'title': 'Lists and Tuples', 'completed': True, 'duration': '40 min'},
            {'id': 6, 'title': 'Dictionaries', 'completed': True, 'duration': '45 min'},
            {'id': 7, 'title': 'File Handling', 'completed': True, 'duration': '50 min'},
            {'id': 8, 'title': 'Exception Handling', 'completed': True, 'duration': '40 min'},
            {'id': 9, 'title': 'Classes and Objects', 'completed': True, 'duration': '60 min'},
            {'id': 10, 'title': 'Inheritance', 'completed': True, 'duration': '50 min'},
            {'id': 11, 'title': 'Modules and Packages', 'completed': False, 'duration': '45 min'},
            {'id': 12, 'title': 'Final Project', 'completed': False, 'duration': '120 min'},
        ],
        'quizzes': [
            {'id': 1, 'title': 'Python Basics Quiz', 'score': 90, 'status': 'Completed', 'date': '2024-01-10'},
            {'id': 2, 'title': 'Python Functions Quiz', 'score': 85, 'status': 'Completed', 'date': '2024-01-15'},
            {'id': 3, 'title': 'Advanced Python', 'score': None, 'status': 'Pending', 'date': None},
        ]
    }
    
    context = {
        'course': course,
        'user': request.user,
    }
    return render(request, 'core/student_course_detail.html', context)


# ============================================
# STUDENT - QUIZ VIEWS
# ============================================

@login_required
def student_quizzes(request):
    """View all quizzes available for the student"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Sample quiz data - In production, fetch from database
    available_quizzes = [
        {
            'id': 1,
            'title': 'Python Basics Quiz',
            'course': 'Python Programming',
            'questions': 20,
            'difficulty': 'Beginner',
            'time_limit': 30,
            'status': 'Available',
            'deadline': datetime(2024, 2, 15),
            'attempts': 2,
            'best_score': 90,
        },
        {
            'id': 2,
            'title': 'ML Concepts Quiz',
            'course': 'Machine Learning Fundamentals',
            'questions': 15,
            'difficulty': 'Intermediate',
            'time_limit': 25,
            'status': 'Available',
            'deadline': datetime(2024, 2, 20),
            'attempts': 1,
            'best_score': 78,
        },
        {
            'id': 3,
            'title': 'HTML/CSS Basics',
            'course': 'Web Development with Django',
            'questions': 25,
            'difficulty': 'Beginner',
            'time_limit': 20,
            'status': 'Completed',
            'deadline': datetime(2024, 1, 30),
            'attempts': 3,
            'best_score': 95,
        },
        {
            'id': 4,
            'title': 'Advanced Python',
            'course': 'Python Programming',
            'questions': 30,
            'difficulty': 'Advanced',
            'time_limit': 45,
            'status': 'Locked',
            'deadline': None,
            'attempts': 0,
            'best_score': None,
        },
        {
            'id': 5,
            'title': 'Data Analysis Quiz',
            'course': 'Data Science & Analytics',
            'questions': 18,
            'difficulty': 'Intermediate',
            'time_limit': 30,
            'status': 'Available',
            'deadline': datetime(2024, 3, 1),
            'attempts': 0,
            'best_score': None,
        },
        {
            'id': 6,
            'title': 'Neural Networks Quiz',
            'course': 'Artificial Intelligence Fundamentals',
            'questions': 22,
            'difficulty': 'Advanced',
            'time_limit': 40,
            'status': 'Available',
            'deadline': datetime(2024, 3, 10),
            'attempts': 0,
            'best_score': None,
        },
    ]
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        available_quizzes = [q for q in available_quizzes if q['status'].lower() == status_filter.lower()]
    
    context = {
        'quizzes': available_quizzes,
        'total_quizzes': len(available_quizzes),
        'available': sum(1 for q in available_quizzes if q['status'] == 'Available'),
        'completed': sum(1 for q in available_quizzes if q['status'] == 'Completed'),
        'locked': sum(1 for q in available_quizzes if q['status'] == 'Locked'),
        'status_filter': status_filter,
        'user': request.user,
    }
    return render(request, 'core/student_quizzes.html', context)


@login_required
def student_take_quiz(request, quiz_id):
    """Take a quiz"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Sample quiz data - In production, fetch from database
    quiz = {
        'id': quiz_id,
        'title': 'Python Basics Quiz',
        'course': 'Python Programming',
        'questions': [
            {
                'id': 1,
                'question': 'What is the output of print(2**3)?',
                'options': ['A) 6', 'B) 8', 'C) 9', 'D) 12'],
                'correct_answer': 1
            },
            {
                'id': 2,
                'question': 'Which keyword is used for function definition in Python?',
                'options': ['A) function', 'B) def', 'C) define', 'D) func'],
                'correct_answer': 1
            },
            {
                'id': 3,
                'question': 'What does the len() function do?',
                'options': ['A) Returns the length of a string', 'B) Returns the length of a list', 'C) Both A and B', 'D) None of the above'],
                'correct_answer': 2
            },
            {
                'id': 4,
                'question': 'How do you create a list in Python?',
                'options': ['A) list = []', 'B) list = {}', 'C) list = ()', 'D) All of the above'],
                'correct_answer': 0
            },
            {
                'id': 5,
                'question': 'What is the correct syntax for a for loop?',
                'options': ['A) for i in range(10):', 'B) for i in range(10)', 'C) for (i=0; i<10; i++)', 'D) for i = 0 to 9'],
                'correct_answer': 0
            },
        ],
        'time_limit': 30,
        'total_questions': 5,
    }
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            answers = data.get('answers', {})
            
            correct = 0
            results = []
            for q in quiz['questions']:
                user_answer = int(answers.get(str(q['id']), -1))
                is_correct = user_answer == q['correct_answer']
                if is_correct:
                    correct += 1
                results.append({
                    'question_id': q['id'],
                    'user_answer': user_answer,
                    'is_correct': is_correct
                })
            
            score = round((correct / len(quiz['questions'])) * 100)
            
            return JsonResponse({
                'success': True,
                'score': score,
                'correct': correct,
                'total': len(quiz['questions']),
                'results': results
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    context = {
        'quiz': quiz,
        'user': request.user,
    }
    return render(request, 'core/student_take_quiz.html', context)


@login_required
def student_quiz_result(request, quiz_id):
    """View quiz results"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Sample result data - In production, fetch from database
    result = {
        'quiz_title': 'Python Basics Quiz',
        'course': 'Python Programming',
        'score': 90,
        'correct': 18,
        'total': 20,
        'time_taken': '15:30',
        'date_taken': datetime(2024, 1, 15),
        'questions': [
            {'number': 1, 'status': 'correct', 'time': '00:45'},
            {'number': 2, 'status': 'correct', 'time': '00:30'},
            {'number': 3, 'status': 'correct', 'time': '00:50'},
            {'number': 4, 'status': 'wrong', 'time': '01:00'},
            {'number': 5, 'status': 'correct', 'time': '00:25'},
            {'number': 6, 'status': 'correct', 'time': '00:40'},
            {'number': 7, 'status': 'correct', 'time': '00:55'},
            {'number': 8, 'status': 'wrong', 'time': '00:35'},
            {'number': 9, 'status': 'correct', 'time': '00:50'},
            {'number': 10, 'status': 'correct', 'time': '00:30'},
            {'number': 11, 'status': 'correct', 'time': '00:45'},
            {'number': 12, 'status': 'correct', 'time': '00:30'},
            {'number': 13, 'status': 'wrong', 'time': '00:50'},
            {'number': 14, 'status': 'correct', 'time': '00:25'},
            {'number': 15, 'status': 'correct', 'time': '00:40'},
            {'number': 16, 'status': 'correct', 'time': '00:30'},
            {'number': 17, 'status': 'correct', 'time': '00:35'},
            {'number': 18, 'status': 'wrong', 'time': '00:45'},
            {'number': 19, 'status': 'correct', 'time': '00:20'},
            {'number': 20, 'status': 'correct', 'time': '00:30'},
        ]
    }
    
    context = {
        'result': result,
        'user': request.user,
    }
    return render(request, 'core/student_quiz_result.html', context)


# ============================================
# STUDENT - PROGRESS VIEWS
# ============================================

@login_required
def student_progress(request):
    """View student progress dashboard"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Sample progress data - In production, fetch from database
    progress = {
        'overall_progress': 65,
        'total_courses': 4,
        'completed_courses': 1,
        'in_progress_courses': 2,
        'total_quizzes_taken': 12,
        'average_score': 85,
        'total_hours': 42,
        'current_streak': 7,
        'total_points': 2450,
        'badges_earned': 5,
        'courses': [
            {'title': 'Python Programming', 'progress': 85, 'status': 'In Progress', 'color': 'primary'},
            {'title': 'Machine Learning Fundamentals', 'progress': 60, 'status': 'In Progress', 'color': 'success'},
            {'title': 'Web Development with Django', 'progress': 100, 'status': 'Completed', 'color': 'success'},
            {'title': 'Data Science & Analytics', 'progress': 30, 'status': 'Not Started', 'color': 'warning'},
        ],
        'weekly_activity': {
            'Mon': 3, 'Tue': 4, 'Wed': 5, 'Thu': 6, 'Fri': 4, 'Sat': 2, 'Sun': 1
        },
        'quiz_performance': [
            {'quiz': 'Python Basics', 'score': 90},
            {'quiz': 'ML Concepts', 'score': 78},
            {'quiz': 'HTML/CSS Basics', 'score': 95},
            {'quiz': 'Advanced Python', 'score': 85},
            {'quiz': 'Data Analysis', 'score': 72},
        ],
        'recent_activity': [
            {'action': 'Completed Python Basics Quiz', 'date': '2 hours ago', 'icon': 'fa-check-circle', 'color': 'success'},
            {'action': 'Started Module 11: Modules and Packages', 'date': '5 hours ago', 'icon': 'fa-play', 'color': 'primary'},
            {'action': 'Earned "Python Master" Badge', 'date': '1 day ago', 'icon': 'fa-trophy', 'color': 'warning'},
            {'action': 'Completed ML Concepts Quiz', 'date': '2 days ago', 'icon': 'fa-check-circle', 'color': 'success'},
            {'action': 'Joined Machine Learning Course', 'date': '3 days ago', 'icon': 'fa-plus-circle', 'color': 'info'},
        ],
        'upcoming_tasks': [
            {'task': 'Complete Python Modules 11-12', 'due': '2 days', 'priority': 'High'},
            {'task': 'Take ML Concepts Quiz', 'due': '5 days', 'priority': 'Medium'},
            {'task': 'Start Data Science Course', 'due': '1 week', 'priority': 'Low'},
        ]
    }
    
    context = {
        'progress': progress,
        'user': request.user,
    }
    return render(request, 'core/student_progress.html', context)


# ============================================
# ADMIN DASHBOARD VIEWS
# ============================================

@login_required
def admin_dashboard(request):
    """Admin dashboard overview with links to all admin features"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    total_users = User.objects.count()
    total_staff = User.objects.filter(is_staff=True).count()
    total_students = total_users - total_staff
    active_users = User.objects.filter(is_active=True).count()
    
    # Sample data - In production, fetch from database
    context = {
        'user': request.user,
        'total_users': total_users,
        'total_students': total_students,
        'total_staff': total_staff,
        'active_users': active_users,
        'total_courses': 5,
        'total_quizzes': 5,
        'published_quizzes': 3,
        'draft_quizzes': 2,
        'total_questions': 108,
        'active_learners': 42,
        'completion_rate': '78%',
        'average_score': '85%',
        'weekly_growth': '12%',
        'popular_course': 'Python Programming',
        'most_active_user': 'john_doe',
        'highest_score': '98%',
        'total_lessons': 156,
        # Quick navigation links
        'admin_students_url': 'admin_students',
        'admin_courses_url': 'admin_courses',
        'admin_quizzes_url': 'admin_quizzes',
        'admin_analytics_url': 'admin_analytics',
    }
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def admin_students(request):
    """Manage students view"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    students_list = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    search_query = request.GET.get('search', '')
    if search_query:
        students_list = students_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    paginator = Paginator(students_list, 10)
    page_number = request.GET.get('page')
    students = paginator.get_page(page_number)
    
    context = {
        'students': students,
        'total_students': User.objects.filter(is_staff=False).count(),
        'active_students': User.objects.filter(is_staff=False, is_active=True).count(),
        'inactive_students': User.objects.filter(is_staff=False, is_active=False).count(),
        'new_this_week': User.objects.filter(
            is_staff=False, 
            date_joined__gte=datetime.now().replace(day=datetime.now().day - 7)
        ).count(),
        'search_query': search_query,
    }
    return render(request, 'core/admin_students.html', context)


@login_required
def admin_student_detail(request, student_id):
    """View student details"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    student = get_object_or_404(User, id=student_id, is_staff=False)
    
    # Sample enrolled courses and quiz history
    enrolled_courses = [
        {'title': 'Python Programming', 'progress': 85, 'status': 'In Progress'},
        {'title': 'Machine Learning', 'progress': 60, 'status': 'In Progress'},
        {'title': 'Web Development', 'progress': 100, 'status': 'Completed'},
    ]
    
    quiz_history = [
        {'title': 'Python Basics', 'score': 90, 'date': '2024-01-15'},
        {'title': 'ML Concepts', 'score': 75, 'date': '2024-01-20'},
        {'title': 'HTML/CSS', 'score': 95, 'date': '2024-01-25'},
    ]
    
    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'quiz_history': quiz_history,
    }
    return render(request, 'core/admin_student_detail.html', context)


@login_required
def admin_student_edit(request, student_id):
    """Edit student"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    student = get_object_or_404(User, id=student_id, is_staff=False)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        is_active = request.POST.get('is_active') == 'on'
        
        if email and User.objects.filter(email=email).exclude(id=student_id).exists():
            messages.error(request, 'Email is already taken.')
            return render(request, 'core/admin_student_edit.html', {'student': student})
        
        student.email = email
        student.first_name = first_name
        student.last_name = last_name
        student.is_active = is_active
        student.save()
        
        messages.success(request, f'Student {student.username} updated successfully.')
        return redirect('admin_students')
    
    return render(request, 'core/admin_student_edit.html', {'student': student})


@csrf_exempt
@require_POST
@login_required
def admin_student_toggle(request, student_id):
    """Toggle student active status via AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        student = User.objects.get(id=student_id, is_staff=False)
        student.is_active = not student.is_active
        student.save()
        return JsonResponse({
            'success': True, 
            'active': student.is_active,
            'message': f'Student {student.username} {"activated" if student.is_active else "deactivated"}'
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
@login_required
def admin_student_delete(request, student_id):
    """Delete student via AJAX"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        student = User.objects.get(id=student_id, is_staff=False)
        username = student.username
        student.delete()
        return JsonResponse({'success': True, 'message': f'Student {username} deleted successfully'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'Student not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def admin_courses(request):
    """Manage courses view"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    courses = [
        {
            'id': 1, 
            'title': 'Python Programming', 
            'description': 'Learn Python from scratch with hands-on projects.',
            'students': 45, 
            'status': 'Active',
            'quizzes': 8,
            'duration': '12',
            'created_at': datetime(2024, 1, 15),
            'instructor': 'Dr. Smith',
            'level': 'Beginner',
            'rating': 4.8,
        },
        {
            'id': 2, 
            'title': 'Machine Learning Fundamentals', 
            'description': 'Introduction to ML concepts and algorithms.',
            'students': 32, 
            'status': 'Active',
            'quizzes': 6,
            'duration': '15',
            'created_at': datetime(2024, 2, 1),
            'instructor': 'Prof. Johnson',
            'level': 'Intermediate',
            'rating': 4.9,
        },
        {
            'id': 3, 
            'title': 'Web Development with Django', 
            'description': 'Build full-stack web applications using Django.',
            'students': 28, 
            'status': 'Draft',
            'quizzes': 5,
            'duration': '10',
            'created_at': datetime(2024, 3, 10),
            'instructor': 'Ms. Williams',
            'level': 'Intermediate',
            'rating': 4.7,
        },
        {
            'id': 4, 
            'title': 'Data Science & Analytics', 
            'description': 'Data analysis and visualization using Python.',
            'students': 19, 
            'status': 'Active',
            'quizzes': 7,
            'duration': '14',
            'created_at': datetime(2024, 4, 5),
            'instructor': 'Dr. Chen',
            'level': 'Advanced',
            'rating': 4.6,
        },
        {
            'id': 5, 
            'title': 'Artificial Intelligence Fundamentals', 
            'description': 'Introduction to AI, neural networks, and deep learning.',
            'students': 15, 
            'status': 'Archived',
            'quizzes': 4,
            'duration': '8',
            'created_at': datetime(2024, 5, 20),
            'instructor': 'Prof. Davis',
            'level': 'Advanced',
            'rating': 4.9,
        },
    ]
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        courses = [c for c in courses if c['status'].lower() == status_filter.lower()]
    
    context = {
        'courses': courses,
        'total_courses': len(courses),
        'active_courses': sum(1 for c in courses if c['status'] == 'Active'),
        'draft_courses': sum(1 for c in courses if c['status'] == 'Draft'),
        'archived_courses': sum(1 for c in courses if c['status'] == 'Archived'),
        'total_students': sum(c['students'] for c in courses),
        'status_filter': status_filter,
    }
    return render(request, 'core/admin_courses.html', context)


@login_required
def admin_course_create(request):
    """Create a new course"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        messages.success(request, 'Course created successfully!')
        return redirect('admin_courses')
    
    return render(request, 'core/admin_course_form.html', {'action': 'Create'})


@login_required
def admin_course_edit(request, course_id):
    """Edit a course"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    course = {
        'id': course_id,
        'title': 'Python Programming',
        'description': 'Learn Python from scratch',
        'level': 'Beginner',
        'duration': '12',
        'status': 'Active',
    }
    
    if request.method == 'POST':
        messages.success(request, 'Course updated successfully!')
        return redirect('admin_courses')
    
    return render(request, 'core/admin_course_form.html', {
        'action': 'Edit',
        'course': course
    })


@login_required
def admin_course_delete(request, course_id):
    """Delete a course"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({
        'success': True, 
        'message': f'Course #{course_id} deleted successfully'
    })


@login_required
def admin_quizzes(request):
    """Manage quizzes view"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    quizzes = [
        {
            'id': 1, 
            'title': 'Python Basics Quiz', 
            'course': 'Python Programming',
            'questions': 20, 
            'difficulty': 'Beginner', 
            'status': 'Published',
            'created_at': datetime(2024, 1, 20),
            'attempts': 45,
            'average_score': 82,
            'time_limit': 30,
        },
        {
            'id': 2, 
            'title': 'ML Concepts Quiz', 
            'course': 'Machine Learning Fundamentals',
            'questions': 15, 
            'difficulty': 'Intermediate', 
            'status': 'Published',
            'created_at': datetime(2024, 2, 15),
            'attempts': 32,
            'average_score': 78,
            'time_limit': 25,
        },
        {
            'id': 3, 
            'title': 'HTML/CSS Basics', 
            'course': 'Web Development with Django',
            'questions': 25, 
            'difficulty': 'Beginner', 
            'status': 'Draft',
            'created_at': datetime(2024, 3, 20),
            'attempts': 0,
            'average_score': 0,
            'time_limit': 20,
        },
        {
            'id': 4, 
            'title': 'Advanced Python', 
            'course': 'Python Programming',
            'questions': 30, 
            'difficulty': 'Advanced', 
            'status': 'Published',
            'created_at': datetime(2024, 4, 10),
            'attempts': 28,
            'average_score': 85,
            'time_limit': 45,
        },
        {
            'id': 5, 
            'title': 'Data Analysis Quiz', 
            'course': 'Data Science & Analytics',
            'questions': 18, 
            'difficulty': 'Intermediate', 
            'status': 'Draft',
            'created_at': datetime(2024, 5, 1),
            'attempts': 0,
            'average_score': 0,
            'time_limit': 30,
        },
    ]
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        quizzes = [q for q in quizzes if q['status'].lower() == status_filter.lower()]
    
    context = {
        'quizzes': quizzes,
        'total_quizzes': len(quizzes),
        'published_quizzes': sum(1 for q in quizzes if q['status'] == 'Published'),
        'draft_quizzes': sum(1 for q in quizzes if q['status'] == 'Draft'),
        'total_questions': sum(q['questions'] for q in quizzes),
        'total_attempts': sum(q['attempts'] for q in quizzes),
        'status_filter': status_filter,
    }
    return render(request, 'core/admin_quizzes.html', context)


@login_required
def admin_quiz_create(request):
    """Create a new quiz"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    courses = ['Python Programming', 'Machine Learning Fundamentals', 'Web Development with Django', 'Data Science & Analytics', 'Artificial Intelligence Fundamentals']
    
    if request.method == 'POST':
        messages.success(request, 'Quiz created successfully!')
        return redirect('admin_quizzes')
    
    return render(request, 'core/admin_quiz_form.html', {
        'action': 'Create',
        'courses': courses,
    })


@login_required
def admin_quiz_edit(request, quiz_id):
    """Edit a quiz"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    quiz = {
        'id': quiz_id,
        'title': 'Python Basics Quiz',
        'course': 'Python Programming',
        'questions': 20,
        'difficulty': 'Beginner',
        'status': 'Published',
        'time_limit': 30,
    }
    
    courses = ['Python Programming', 'Machine Learning Fundamentals', 'Web Development with Django', 'Data Science & Analytics', 'Artificial Intelligence Fundamentals']
    
    if request.method == 'POST':
        messages.success(request, 'Quiz updated successfully!')
        return redirect('admin_quizzes')
    
    return render(request, 'core/admin_quiz_form.html', {
        'action': 'Edit',
        'quiz': quiz,
        'courses': courses,
    })


@login_required
def admin_quiz_delete(request, quiz_id):
    """Delete a quiz"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    return JsonResponse({
        'success': True, 
        'message': f'Quiz #{quiz_id} deleted successfully'
    })


@login_required
def admin_quiz_questions(request, quiz_id):
    """Manage quiz questions"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    questions = [
        {'id': 1, 'text': 'What is the output of print(2**3)?', 'type': 'MCQ', 'difficulty': 'Beginner'},
        {'id': 2, 'text': 'Which keyword is used for function definition?', 'type': 'MCQ', 'difficulty': 'Beginner'},
        {'id': 3, 'text': 'What does the len() function do?', 'type': 'MCQ', 'difficulty': 'Easy'},
        {'id': 4, 'text': 'How do you create a list in Python?', 'type': 'MCQ', 'difficulty': 'Easy'},
        {'id': 5, 'text': 'What is the correct syntax for a for loop?', 'type': 'MCQ', 'difficulty': 'Intermediate'},
    ]
    
    context = {
        'quiz_id': quiz_id,
        'questions': questions,
        'total_questions': len(questions),
    }
    return render(request, 'core/admin_quiz_questions.html', context)


@login_required
def admin_analytics(request):
    """Analytics dashboard view"""
    if not request.user.is_staff:
        return redirect('dashboard')
    
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True, last_login__isnull=False).count()
    total_students = User.objects.filter(is_staff=False).count()
    total_instructors = User.objects.filter(is_staff=True).count()
    
    analytics = {
        'total_users': total_users,
        'active_users': active_users,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'total_courses': 5,
        'total_quizzes': 5,
        'total_questions': 108,
        'completion_rate': '78%',
        'average_score': '85%',
        'weekly_growth': '12%',
        'popular_course': 'Python Programming',
        'most_active_user': 'john_doe',
        'highest_score': '98%',
        'total_lessons': 156,
        'daily_active': 35,
        'monthly_growth': '8%',
        'engagement_rate': '76%',
        'weekly_activity': {
            'Mon': 65, 'Tue': 78, 'Wed': 82, 'Thu': 90, 'Fri': 85, 'Sat': 55, 'Sun': 40
        },
        'course_enrollment': {
            'Python Programming': 45,
            'Machine Learning': 32,
            'Web Development': 28,
            'Data Science': 19,
            'AI Fundamentals': 15
        },
        'quiz_performance': {
            'Python Basics': 82,
            'ML Concepts': 78,
            'Advanced Python': 85,
            'Neural Networks': 72,
        },
    }
    
    return render(request, 'core/admin_analytics.html', {'analytics': analytics})


# ============================================
# API ENDPOINTS
# ============================================

def api_analytics_data(request):
    """API endpoint for analytics charts"""
    data = {
        'weekly_activity': {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'values': [65, 78, 82, 90, 85, 55, 40]
        },
        'course_enrollment': {
            'labels': ['Python', 'ML', 'Web Dev', 'Data Science', 'AI'],
            'values': [45, 32, 28, 19, 15]
        },
        'quiz_performance': {
            'labels': ['Python Basics', 'ML Concepts', 'Advanced Python', 'Neural Networks'],
            'values': [82, 78, 85, 72]
        }
    }
    return JsonResponse(data)


def api_stats(request):
    """API endpoint to get platform statistics"""
    stats = {
        'total_users': User.objects.count(),
        'total_courses': 5,
        'total_quizzes': 5,
        'active_users': User.objects.filter(is_active=True).count(),
    }
    return JsonResponse(stats)