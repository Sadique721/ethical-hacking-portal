from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from . import views

router = DefaultRouter()
router.register('profiles', views.ProfileViewSet, basename='api-profiles')
router.register('ctf/challenges', views.ChallengeViewSet, basename='api-challenges')

urlpatterns = [
    # Router endpoints
    path('', include(router.urls)),
    
    # Custom endpoints
    path('cve/search/', views.CVESearchView.as_view(), name='api-cve-search'),
    path('headers/analyze/', views.HeaderAnalyzerView.as_view(), name='api-header-analyze'),
    
    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # OpenAPI Schema & Swagger Docs
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
