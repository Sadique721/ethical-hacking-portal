from django.urls import path
from . import views

urlpatterns = [
    path('cve/', views.cve_lookup, name='cve_lookup'),
    path('headers/', views.header_analyzer, name='header_analyzer'),
    path('report/', views.generate_report, name='generate_report'),
]
