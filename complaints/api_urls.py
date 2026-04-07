from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import ComplaintViewSet, CategoryViewSet, CustomAuthToken

router = DefaultRouter()
router.register(r'complaints', ComplaintViewSet, basename='api-complaints')
router.register(r'categories', CategoryViewSet, basename='api-categories')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', CustomAuthToken.as_view(), name='api-token'),
]