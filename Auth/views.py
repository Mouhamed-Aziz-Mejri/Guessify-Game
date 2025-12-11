from django.shortcuts import render, redirect
from guesser.models import GameSession, Answer
import numpy as np
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        
        # Validation
        if not username or not email or not password:
            return render(request, 'registration/signup.html', {
                'error': 'All fields are required!'
            })
        
        if len(username) < 3:
            return render(request, 'signup.html', {
                'error': 'Username must be at least 3 characters long!'
            })
        
        if len(password) < 8:
            return render(request, 'registration/signup.html', {
                'error': 'Password must be at least 8 characters long!'
            })
        
        if password != confirm_password:
            return render(request, 'registration/signup.html', {
                'error': 'Passwords do not match!'
            })
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return render(request, 'registration/signup.html', {
                'error': 'Username already taken!'
            })
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return render(request, 'registration/signup.html', {
                'error': 'Email already registered!'
            })
        
        try:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.save()
            
            # Log the user in
            login(request, user)
            
            messages.success(request, 'Account created successfully! Welcome to Celebrity Guesser!')
            return redirect('home')
            
        except IntegrityError:
            return render(request, 'registration/signup.html', {
                'error': 'An error occurred. Please try again.'
            })
    
    return render(request, 'registration/signup.html')

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember = request.POST.get('remember')
        
        if not username or not password:
            return render(request, 'login.html', {
                'error': 'Please enter both username and password!'
            })
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login successful
            login(request, user)
            
            # Handle "Remember Me"
            if not remember:
                # Session expires when browser closes
                request.session.set_expiry(0)
            else:
                # Session expires in 2 weeks
                request.session.set_expiry(1209600)  # 2 weeks in seconds
            
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next page or home
            next_page = request.GET.get('next', 'home')
            return redirect(next_page)
        else:
            return render(request, 'registration/login.html', {
                'error': 'Invalid username or password!'
            })
    
    return render(request, 'registration/login.html')


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, f'You have been logged out successfully.')
    return redirect('login')

@login_required(login_url='login')
def profile_view(request):
    """User profile view"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user's game statistics (only games associated with this user)
    user_sessions = GameSession.objects.filter(user=request.user)
    
    total_games = user_sessions.filter(is_completed=True).count()
    correct_guesses = user_sessions.filter(is_completed=True, is_correct=True).count()
    win_rate = round((correct_guesses / total_games * 100)) if total_games > 0 else 0
    
    # Get recent games (last 10)
    recent_games = user_sessions.filter(is_completed=True).order_by('-created_at')[:10]
    
    context = {
        'user': request.user,
        'total_games': total_games,
        'correct_guesses': correct_guesses,
        'win_rate': win_rate,
        'recent_games': recent_games,
    }
    
    return render(request, 'profile.html', context)