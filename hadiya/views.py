from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser


def login_page(request):
    """
    Handle user login with email-based authentication
    """
    if request.user.is_authenticated:
        return redirect_user_by_type(request.user)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate using email (custom backend handles this)
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name}!')
            return redirect_user_by_type(user)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    return render(request, 'login.html')


def logout_user(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def redirect_user_by_type(user):
    """
    Redirect users to appropriate dashboard based on user_type
    1 = HOD, 2 = Staff, 3 = Student, 4 = Accountant
    """
    if user.user_type == 1:  # HOD
        return redirect('hod_dashboard')
    elif user.user_type == 2:  # Staff
        return redirect('staff_home')
    elif user.user_type == 3:  # Student
        return redirect('student_home')
    elif user.user_type == 4:  # Accountant
        return redirect('accountant_dashboard')
    elif user.user_type == 5:   # Management
        return redirect('management_dashboard')
    else:
        return redirect('login')


def home(request):
    """
    Landing page - public access
    Authenticated users are redirected to dashboard
    """
    if request.user.is_authenticated:
        return redirect_user_by_type(request.user)
    
    return render(request, 'landing.html')
