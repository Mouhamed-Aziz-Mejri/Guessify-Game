from django.contrib import admin
from .models import GameSession, Answer

@admin.register(GameSession)
class GameSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'created_at', 'is_completed', 'guessed_celebrity', 'is_correct']
    list_filter = ['is_completed', 'is_correct', 'created_at']
    search_fields = ['session_key', 'guessed_celebrity']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['game_session', 'feature', 'answer', 'created_at']
    list_filter = ['answer', 'created_at']
    search_fields = ['feature']
    