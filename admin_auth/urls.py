from django.contrib import admin
from django.urls import path, include
from admin_auth import views

urlpatterns = [
    path('start/', views.admin_dashboard, name='start'),
    path('nb_users/', views.admin_dashboard, name='nb_users'),
    path('nb_games/', views.admin_dashboard, name='nb_games'),
path('users_list/',views.admin_users,name='users_list'),
path('games_list/',views.admin_games,name='games_list'),
path('games_list/<int:game_id>/answers/', views.game_answers, name='game_answers'),  
    path('games/<int:game_id>/delete/', views.delete_game, name='delete_game'),  

    # User management endpoints
    path('users/<int:user_id>/details/', views.user_details, name='user_details'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/create/', views.create_user, name='create_user'),
]
