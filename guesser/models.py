from django.db import models
from django.contrib.auth.models import User
import json

class GameSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Add this
    session_key = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_completed = models.BooleanField(default=False)
    guessed_celebrity = models.CharField(max_length=100, blank=True, null=True)
    is_correct = models.BooleanField(default=False, null=True, blank=True)
    
    def __str__(self):
        if self.user:
            return f"Session by {self.user.username} - {self.created_at}"
        return f"Session {self.session_key} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']

class Answer(models.Model):
    game_session = models.ForeignKey(GameSession, on_delete=models.CASCADE, related_name='answers')
    feature = models.CharField(max_length=100)
    answer = models.CharField(max_length=10)  # 'yes' or 'no'
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.feature}: {self.answer}"
    
    class Meta:
        ordering = ['created_at']