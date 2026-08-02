from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='challenges_list', permanent=False)),
    path('challenges/', views.challenges_list, name='challenges_list'),
    path('submit/<int:challenge_id>/', views.submit_flag, name='submit_flag'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
