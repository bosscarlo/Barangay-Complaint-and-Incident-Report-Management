from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('complaints/', views.complaint_list, name='complaint_list'),
    path('complaints/new/', views.complaint_create, name='complaint_create'),
    path('complaints/<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('complaints/<int:pk>/edit/', views.complaint_edit, name='complaint_edit'),
]