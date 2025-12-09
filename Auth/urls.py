from django.urls import path
from django.views.generic import TemplateView
from Auth import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('h/',TemplateView.as_view(template_name='home_auth.html'),name='home_auth'),
   path('signup/', views.signup_view, name='signup'),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
