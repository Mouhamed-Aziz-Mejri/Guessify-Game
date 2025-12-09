from django.shortcuts import render, redirect
from django.http import JsonResponse

import guesser
import guesser.data
from .models import GameSession, Answer
from .utils import get_guesser
import uuid
import numpy as np
import logging
import pandas as pd
from django.contrib.auth.decorators import login_required

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@login_required(login_url='login')  # Add this decorator

def home(request):
    """Home page - Start new game"""
    # Calculate GLOBAL statistics (all users)
    total_games = GameSession.objects.filter(is_completed=True).count()
    correct_guesses = GameSession.objects.filter(is_completed=True, is_correct=True).count()
    
    # Calculate win rate
    if total_games > 0:
        win_rate = round((correct_guesses / total_games) * 100)
    else:
        win_rate = 0
    
    # If user is logged in, also get their personal stats
    user_stats = None
    if request.user.is_authenticated:
        user_sessions = GameSession.objects.filter(user=request.user, is_completed=True)
        user_total = user_sessions.count()
        user_correct = user_sessions.filter(is_correct=True).count()
        user_win_rate = round((user_correct / user_total * 100)) if user_total > 0 else 0
        
        user_stats = {
            'total_games': user_total,
            'correct_guesses': user_correct,
            'win_rate': user_win_rate,
        }
    data=pd.read_csv('guesser/data/guessify_simple.csv')
    context = {
        'total_celebrities': len(data),  # Update this if you add more celebrities
        'total_games': total_games,  # Global stats
        'win_rate': win_rate,  # Global win rate
        'user_stats': user_stats,  # Personal stats for logged-in users
    }
    
    return render(request, 'home.html', context)
@login_required(login_url='login')
def start_game(request):
    """Start a new game session"""
    # Generate unique session key
    if request.user.is_authenticated:
        # For logged-in users, include user ID in session key
        session_key = f"user_{request.user.id}_{str(uuid.uuid4())}"
        
        # Create new game session with user association
        game_session = GameSession.objects.create(
            session_key=session_key,
            user=request.user  # Associate with user
        )
    else:
        # For anonymous users
        session_key = str(uuid.uuid4())
        game_session = GameSession.objects.create(session_key=session_key)
    
    # Store session key in Django session
    request.session['game_session_key'] = session_key
    
    return redirect('play_game')
@login_required(login_url='login')
def play_game(request):
    """Main game page - Ask questions"""
    # Get current game session
    session_key = request.session.get('game_session_key')
    
    if not session_key:
        return redirect('home')
    
    try:
        game_session = GameSession.objects.get(session_key=session_key)
    except GameSession.DoesNotExist:
        return redirect('home')
    
    # If game is completed, redirect to result
    if game_session.is_completed:
        return redirect('result')
    
    # Get the guesser
    guesser = get_guesser()
    
    # Get all answered features
    answered = game_session.answers.all()
    answered_features = {ans.feature for ans in answered}
    
    # Calculate remaining celebrities based on answers
    answers_dict = {ans.feature: ans.answer for ans in answered}
    remaining_celebrities = calculate_remaining_celebrities(guesser, answers_dict)
    
    # Get next question
    next_feature = guesser.get_next_question(answered_features)
    
    # Decision logic for when to guess
    # Decision logic for when to guess
    min_questions = 5
    max_questions = 10
    current_question_count = len(answered)

    # Determine if we should make a guess
    should_guess = False

    if current_question_count >= max_questions:
        # Always guess at maximum questions
        should_guess = True
    elif current_question_count >= min_questions:
        # After minimum questions, guess if:
        # 1. No more questions available, OR
        # 2. Exactly 1 celebrity matches
        if next_feature is None or remaining_celebrities == 1:
            should_guess = True
    elif remaining_celebrities == 1:
        # If we narrowed down to exactly 1, guess immediately (even before min questions)
        should_guess = True

    # If no question available and haven't reached min, force guess
    if next_feature is None and current_question_count < min_questions:
        should_guess = True
        
    if should_guess:
        print("\n" + "🎯"*40)
        print("🔮 MAKING FINAL PREDICTION...")
        print("🎯"*40 + "\n")
        
        # Refresh answers_dict to include all answers
        all_answers = game_session.answers.all()
        answers_dict = {ans.feature: ans.answer for ans in all_answers}
        
        print("📋 FINAL ANSWERS SUMMARY:")
        print("-" * 80)
        for feature, answer in answers_dict.items():
            question = guesser.format_feature_question(feature)
            print(f"   {question} → {answer.upper()}")
        print("-" * 80 + "\n")
        
        # STRICT FILTERING: Only consider celebrities that match ALL answers
        filtered_celebrities = guesser.data.copy()
        
        print("🔎 FILTERING PROCESS:")
        total_start = len(filtered_celebrities)
        
        for feature, answer in answers_dict.items():
            if feature in guesser.feature_names:
                before = len(filtered_celebrities)
                if answer == 'yes':
                    filtered_celebrities = filtered_celebrities[filtered_celebrities[feature] == 1]
                elif answer == 'no':
                    filtered_celebrities = filtered_celebrities[filtered_celebrities[feature] == 0]
                after = len(filtered_celebrities)
                
                if before != after:
                    print(f"   • {feature} = {answer}: {before} → {after} celebrities")
        
        # print(f"\n📊 FILTERING RESULTS:")
        # print(f"   Started with: {total_start} celebrities")
        # print(f"   After filtering: {len(filtered_celebrities)} celebrities")
        
        # Check if we found any matches
        if len(filtered_celebrities) > 0:
            print(f"\n✅ MATCHES FOUND:")
            for idx, name in enumerate(filtered_celebrities['name'].tolist(), 1):
                print(f"   {idx}. {name}")
            
            # If multiple matches, pick the most likely one using the model
            if len(filtered_celebrities) > 1:
                print(f"\n🤖 Using AI to pick best match from {len(filtered_celebrities)} options...")
                
                feature_vector = []
                for feature in guesser.feature_names:
                    if feature in answers_dict:
                        feature_vector.append(1 if answers_dict[feature] == 'yes' else 0)
                    else:
                        feature_vector.append(0)
                
                feature_vector = np.array(feature_vector).reshape(1, -1)
                
                try:
                    probabilities = guesser.model.predict_proba(feature_vector)[0]
                    classes = guesser.model.classes_
                    
                    # Find best match among filtered celebrities
                    best_match = None
                    best_prob = 0
                    
                    for idx, celebrity in enumerate(classes):
                        if celebrity in filtered_celebrities['name'].values:
                            prob = probabilities[idx]
                            print(f"   • {celebrity}: {prob*100:.2f}% confidence")
                            if prob > best_prob:
                                best_prob = prob
                                best_match = celebrity
                    
                    guessed_name = best_match if best_match else filtered_celebrities.iloc[0]['name']
                    print(f"\n🏆 AI picked: {guessed_name} (Confidence: {best_prob*100:.2f}%)")
                except Exception as e:
                    print(f"\n⚠️  AI prediction failed: {e}")
                    guessed_name = filtered_celebrities.iloc[0]['name']
                    print(f"   Fallback: Picking first match → {guessed_name}")
            else:
                # Only one match - perfect!
                guessed_name = filtered_celebrities.iloc[0]['name']
                print(f"\n🎉 PERFECT MATCH! Only one celebrity fits: {guessed_name}")
        else:
            # NO MATCHES FOUND
            guessed_name = "No celebrity matches your answers"
            print(f"\n❌ NO MATCH FOUND!")
            print("   None of our celebrities match ALL your answers.")
        
        print(f"\n🎯 FINAL GUESS: {guessed_name}")
        print("🎯"*40 + "\n")
        
        # Save prediction
        game_session.guessed_celebrity = guessed_name
        game_session.is_completed = True
        game_session.save()
        
        return redirect('result')
    
    # Format the question
    question = guesser.format_feature_question(next_feature)
    
    # Calculate progress percentage based on remaining celebrities
    total_celebrities = len(guesser.data)
    narrowed_down = total_celebrities - remaining_celebrities
    progress_percentage = (narrowed_down / total_celebrities) * 100
    
    # Ensure progress is at least visible after first question
    if len(answered) > 0 and progress_percentage < 5:
        progress_percentage = 5
    
    # Cap at 95% until final guess
    if progress_percentage > 95:
        progress_percentage = 95
    
    context = {
        'question': question,
        'feature': next_feature,
        'question_number': len(answered) + 1,
        'total_questions': 10,
        'remaining_celebrities': remaining_celebrities,
        'progress_percentage': progress_percentage
    }
    
    return render(request, 'play_game.html', context)
def predict_with_filtering(self, answers):
    """
    Predict celebrity based on answers with strict filtering
    """
    if self.model is None:
        return None
    
    # First, filter the dataset based on exact answers
    filtered_data = self.data.copy()
    
    for feature, answer in answers.items():
        if feature in self.feature_names:
            if answer == 'yes':
                filtered_data = filtered_data[filtered_data[feature] == 1]
            elif answer == 'no':
                filtered_data = filtered_data[filtered_data[feature] == 0]
            # 'unknown', 'probably', 'probably_not' don't filter strictly
    
    # If we have exact matches, return the best one
    if len(filtered_data) > 0:
        # If only one match, return it with high confidence
        if len(filtered_data) == 1:
            return {
                'name': filtered_data.iloc[0]['name'],
                'confidence': 1.0
            }
        
        # Multiple matches - use the model to pick the best one
        # Create feature vector
        feature_vector = []
        for feature in self.feature_names:
            if feature in answers:
                feature_vector.append(1 if answers[feature] == 'yes' else 0)
            else:
                feature_vector.append(0)
        
        feature_vector = np.array(feature_vector).reshape(1, -1)
        
        # Get probabilities for all celebrities
        probabilities = self.model.predict_proba(feature_vector)[0]
        classes = self.model.classes_
        
        # Find the best match among filtered celebrities
        best_match = None
        best_prob = 0
        
        for idx, celebrity in enumerate(classes):
            if celebrity in filtered_data['name'].values:
                if probabilities[idx] > best_prob:
                    best_prob = probabilities[idx]
                    best_match = celebrity
        
        if best_match:
            return {
                'name': best_match,
                'confidence': best_prob
            }
    
    # Fallback: use regular prediction if no filtered matches
    return self.predict(answers)
def calculate_remaining_celebrities(guesser, answers_dict):
    """Calculate how many celebrities match the current answers"""
    if not answers_dict:
        return len(guesser.data)
    
    # Start with all celebrities
    remaining = guesser.data.copy()
    
    # Filter based on answers - only filter for clear yes/no answers
    for feature, answer in answers_dict.items():
        if feature in guesser.feature_names:
            if answer == 'yes':
                # Only keep celebrities where this feature is yes (1)
                remaining = remaining[remaining[feature] == 1]
            elif answer == 'no':
                # Only keep celebrities where this feature is no (0)
                remaining = remaining[remaining[feature] == 0]
            # For 'unknown', 'probably', 'probably_not' we don't filter
    
    # Return actual count (can be 0)
    return len(remaining)

@login_required(login_url='login')
def submit_answer(request):
    """Submit answer to current question"""
    if request.method == 'POST':
        session_key = request.session.get('game_session_key')
        
        if not session_key:
            return redirect('home')
        
        try:
            game_session = GameSession.objects.get(session_key=session_key)
        except GameSession.DoesNotExist:
            return redirect('home')
        
        # Get answer from POST data
        feature = request.POST.get('feature')
        answer = request.POST.get('answer')  # 'yes', 'no', 'unknown', 'probably', 'probably_not'
        
        # Convert answer types for prediction
        if answer == 'probably':
            final_answer = 'yes'
        elif answer == 'probably_not':
            final_answer = 'no'
        elif answer == 'unknown':
            final_answer = 'no'  # Treat unknown as no for filtering
        else:
            final_answer = answer
        
        # Save answer
        Answer.objects.create(
            game_session=game_session,
            feature=feature,
            answer=final_answer
        )
        
        # Get guesser for formatting question
        # guesser = get_guesser()
        # question_text = guesser.format_feature_question(feature)
        
        # # LOG THE ANSWER
        # print("\n" + "="*80)
        # print(f"🎯 QUESTION ANSWERED:")
        # print(f"   Question: {question_text}")
        # print(f"   Feature: {feature}")
        # print(f"   User Answer: {answer} → Stored as: {final_answer}")
        # print(f"   Question #: {game_session.answers.count()}")
        # print("="*80 + "\n")
        
        return redirect('play_game')
    
    return redirect('home')
@login_required(login_url='login')
def result(request):
    """Show the final guess"""
    session_key = request.session.get('game_session_key')
    
    if not session_key:
        return redirect('home')
    
    try:
        game_session = GameSession.objects.get(session_key=session_key)
    except GameSession.DoesNotExist:
        return redirect('home')
    
    if not game_session.is_completed:
        return redirect('play_game')
    
    # Get the guesser and calculate confidence
    guesser = get_guesser()
    answers_dict = {ans.feature: ans.answer for ans in game_session.answers.all()}
    
    # Get prediction with confidence
    prediction = guesser.predict_with_filtering(answers_dict)
    confidence = prediction['confidence'] * 100  # Convert to percentage
    
    # Count questions asked
    questions_asked = game_session.answers.count()
    
    # Calculate remaining celebrities
    remaining_celebrities = calculate_remaining_celebrities(guesser, answers_dict)
    
    context = {
        'guessed_celebrity': game_session.guessed_celebrity,
        'is_correct': game_session.is_correct,
        'confidence': confidence,
        'questions_asked': questions_asked,
        'remaining_celebrities': remaining_celebrities
    }
    
    return render(request, 'result.html', context)
@login_required(login_url='login')
def confirm_result(request):
    
    """User confirms if the guess was correct or not"""
    if request.method == 'POST':
        session_key = request.session.get('game_session_key')
        
        if session_key:
            try:
                game_session = GameSession.objects.get(session_key=session_key)
                is_correct = request.POST.get('is_correct') == 'yes'
                game_session.is_correct = is_correct
                game_session.save()
            except GameSession.DoesNotExist:
                pass
        
        # Clear session
        request.session.pop('game_session_key', None)
        
        return redirect('home')
    
    return redirect('home')


def characters_list(request):
    """Show all celebrities in the database"""
    from .utils import get_guesser
    import os
    from django.conf import settings
    
    # Get the guesser to access celebrity data
    guesser = get_guesser()
    
    # Convert dataframe to list of dictionaries for template
    celebrities_data = []
    
    for index, row in guesser.data.iterrows():
        # Create a filename-friendly version of the name
        name = row['name']
        image_filename = name.lower().replace(' ', '_').replace('é', 'e').replace('ô', 'o').replace('í', 'i') + '.jpg'
        
        # Check if image exists
        image_path = os.path.join(settings.BASE_DIR, 'guesser', 'static', 'images', 'celebrities', image_filename)
        has_image = os.path.exists(image_path)
        
        celebrity = {
            'name': name,
            'actor': row['actor'] == 1,
            'musician': row['musician'] == 1,
            'athlete': row['athlete'] == 1,
            'entrepreneur': row['entrepreneur'] == 1,
            'politician': row['politician'] == 1,
            'scientist': row['scientist'] == 1,
            'image_filename': image_filename,
            'has_image': has_image,
        }
        celebrities_data.append(celebrity)
    
    # Sort alphabetically
    celebrities_data.sort(key=lambda x: x['name'])
    
    context = {
        'celebrities': celebrities_data,
        'total_celebrities': len(celebrities_data)
    }
    
    return render(request, 'characters_list.html', context)