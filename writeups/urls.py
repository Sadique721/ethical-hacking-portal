from django.urls import path
from . import views

urlpatterns = [
    path('', views.writeups_list, name='writeups_list'),
    path('<int:pk>/', views.writeup_detail, name='writeup_detail'),
]
