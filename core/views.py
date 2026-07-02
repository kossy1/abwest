from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

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

@login_required
def dashboard(request):
    """User dashboard view"""
    return render(request, 'core/dashboard.html', {'user': request.user})

@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_staff:
        return redirect('dashboard')
    return render(request, 'core/admin_dashboard.html', {'user': request.user})