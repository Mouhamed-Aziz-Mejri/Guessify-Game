from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from guesser.models import GameSession
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from guesser.models import GameSession,Answer
# Create your views here.
def admin_dashboard(request):
       # Total games
    total_games = GameSession.objects.count()
    
    # Completed games
    completed_games = GameSession.objects.filter(is_completed=True).count()
    
    # Pending games (started but not completed)
    pending_games = GameSession.objects.filter(is_completed=False).count()
    
    # Correct guesses
    correct_guesses = GameSession.objects.filter(is_completed=True, is_correct=True).count()
    
    # user_sessions = GameSession.objects.all()
    all_users=User.objects.all()[:3]
    recent_games=GameSession.objects.filter(is_completed=True).order_by('-created_at')[:3]
    user_total = User.objects.count()
    # user_correct = user_sessions.filter(is_correct=True).count()
    user_win_rate = round((correct_guesses / total_games * 100)) if user_total > 0 else 0 
    context = {
        'title': 'Number of Games',
        'nb_users':user_total,
        'nb_games': total_games,
        'completed_games': completed_games,

        # 'correct_guesses': user_correct,
        'user_win_rate': user_win_rate,
        'all_users': all_users,
        'recent_games': recent_games,
    }
    return render(request, "admin_dashboard.html",context)

# @staff_member_required(login_url='login')
def admin_users(request):
    """Admin view to manage users"""
    users = User.objects.all().order_by('date_joined')
    
    # Count stats
    staff_count = User.objects.filter(is_staff=True).count()
    active_count = User.objects.filter(is_active=True).count()
    superuser_count = User.objects.filter(is_superuser=True).count()
    
    context = {
        'users': users,
        'staff_count': staff_count,
        'active_count': active_count,
        'superuser_count': superuser_count,
    }
    
    return render(request, 'admin_users.html', context)


#@staff_member_required(login_url='login')
def admin_games(request):
    """Admin view to see all games with user associations"""
    # Get all games ordered by most recent
    games = GameSession.objects.select_related('user').prefetch_related('answers').order_by('-created_at')
    
    # Calculate stats
    total_games = games.count()
    completed_games = games.filter(is_completed=True).count()
    correct_games = games.filter(is_completed=True, is_correct=True).count()
    wrong_games = games.filter(is_completed=True, is_correct=False).count()
    pending_games = games.filter(is_completed=False).count()
    
    # Calculate win rate
    win_rate = round((correct_games / completed_games * 100)) if completed_games > 0 else 0
    
    context = {
        'games': games,
        'total_games': total_games,
        'completed_games': completed_games,
        'correct_games': correct_games,
        'wrong_games': wrong_games,
        'pending_games': pending_games,
        'win_rate': win_rate,
    }
    
    return render(request, 'admin_games.html', context)


@staff_member_required
@require_http_methods(["GET"])
def game_details(request, game_id):
    """Get game details as JSON"""
    try:
        game = get_object_or_404(GameSession, id=game_id)
        
        # Determine result color and text
        if game.is_correct:
            result_color = 'green'
            result_icon = '✓'
            result_text = 'Correct'
        elif game.is_correct == False:
            result_color = 'red'
            result_icon = '✗'
            result_text = 'Wrong'
        else:
            result_color = 'gray'
            result_icon = '—'
            result_text = 'N/A'
        
        data = {
            'success': True,
            'game': {
                'id': game.id,
                'username': game.user.username,
                'email': game.user.email,
                'celebrity': game.guessed_celebrity,
                'questions_count': game.answers.count(),
                'is_completed': game.is_completed,
                'result_color': result_color,
                'result_icon': result_icon,
                'result_text': result_text,
                'created_at': game.created_at.strftime('%B %d, %Y at %I:%M %p'),
            }
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@staff_member_required
@require_http_methods(["GET"])
def game_answers(request, game_id):
    """Get game answers as JSON"""
    try:
        game = get_object_or_404(GameSession, id=game_id)
        answers = game.answers.all().order_by('created_at')
        
        answers_list = []
        for answer in answers:
            answers_list.append({
                'question': answer.question,
                'answer': answer.answer,
                'created_at': answer.created_at.strftime('%I:%M %p'),
            })
        
        data = {
            'success': True,
            'game': {
                'celebrity': game.guessed_celebrity,
                'username': game.user.username,
            },
            'answers': answers_list
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@staff_member_required
@require_http_methods(["POST"])
def delete_game(request, game_id):
    """Delete a game"""
    try:
        game = get_object_or_404(GameSession, id=game_id)
        game.delete()
        return JsonResponse({'success': True, 'message': 'Game deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
@require_http_methods(["GET"])
def game_answers(request, game_id):
    try:
        game = GameSession.objects.get(id=game_id)
        # Change 'game' to 'game_session' to match your model
        answers = Answer.objects.filter(game_session=game).values('id', 'answer', 'feature', 'created_at')
        
        # Build answers with question from feature
        answers_list = []
        for answer in answers:
            answers_list.append({
                'id': answer['id'],
                'question': answer.get('feature', 'Unknown'),  # Assuming 'feature' contains the question
                'answer': answer['answer'],
                'created_at': answer['created_at'].strftime('%Y-%m-%d %H:%M:%S') if answer['created_at'] else ''
            })
        
        return JsonResponse({
            'success': True,
            'game': {
                'celebrity': game.guessed_celebrity,
                'username': game.user.username,
            },
            'answers': answers_list
        })
    except GameSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Game not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# User Details View
@require_http_methods(["GET"])
@login_required
def user_details(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name or '—',
                'last_name': user.last_name or '—',
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
                'date_joined': user.date_joined.strftime('%B %d, %Y at %I:%M %p'),
                'last_login': user.last_login.strftime('%B %d, %Y at %I:%M %p') if user.last_login else 'Never',
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Edit User View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

@require_http_methods(["POST"])
@login_required
def edit_user(request, user_id):
    try:
        # Check if user exists
        user = User.objects.get(id=user_id)
        
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            return JsonResponse({
                'success': False,
                'error': f'Invalid JSON: {str(e)}'
            }, status=400)
        
        # Update user fields
        if 'first_name' in data:
            user.first_name = data['first_name'] or ''
        if 'last_name' in data:
            user.last_name = data['last_name'] or ''
        if 'email' in data:
            user.email = data['email']
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        # Save changes
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'User updated successfully',
            'user': {
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'is_staff': user.is_staff,
                'is_active': user.is_active,
            }
        })
    
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    
    except Exception as e:
        # Log the error for debugging
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)
        
# Delete User View
@require_http_methods(["POST"])
@login_required
@csrf_protect
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        
        # Prevent deleting yourself
        if user.id == request.user.id:
            return JsonResponse({
                'success': False,
                'error': 'You cannot delete your own account'
            }, status=400)
        
        username = user.username
        user.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'User "{username}" deleted successfully'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
        
@require_http_methods(["POST"])
@staff_member_required
def create_user(request):
    try:
        data = json.loads(request.body)
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        is_active = data.get('is_active', True)
        is_staff = data.get('is_staff', False)
        
        # Validation
        if not username or not email or not password:
            return JsonResponse({'success': False, 'error': 'Username, email, and password are required'}, status=400)
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists'}, status=400)
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already exists'}, status=400)
        
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_staff=is_staff
        )
        
        return JsonResponse({
            'success': True,
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)