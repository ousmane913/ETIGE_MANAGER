from django.urls import path
from . import views

urlpatterns = [
    path('health/', views.health_check, name='health'),
    path('', views.dashboard, name='dashboard'),
    path('connexion/', views.login_view, name='login'),
    path('deconnexion/', views.logout_view, name='logout'),
]
