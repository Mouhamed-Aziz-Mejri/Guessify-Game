from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('start/', views.start_game, name='start_game'),
    path('play/', views.play_game, name='play_game'),
    path('submit/', views.submit_answer, name='submit_answer'),
    path('result/', views.result, name='result'),
    path('confirm/', views.confirm_result, name='confirm_result'),
    path("characters_list/",views.characters_list,name="characters_list")
]