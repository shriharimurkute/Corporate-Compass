from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_agency, name='agency_register'),
    path('list/', views.agency_list, name='agency_list'),
    path('dashboard/', views.agency_dashboard, name='agency_dashboard'),
    path('<int:pk>/', views.agency_detail, name='agency_detail'),
    # Add edit/delete URLs if needed
]