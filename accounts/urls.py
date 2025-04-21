from django.urls import path
from . import views

urlpatterns = [
    path('register/user/', views.UserRegisterView.as_view(), name='register_user'),
    path('register/agency/', views.AgencyAdminRegisterView.as_view(), name='register_agency_admin'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard-redirect/', views.dashboard_redirect_view, name='dashboard_redirect'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    # Add profile view URL if needed: path('profile/', views.profile_view, name='profile'),
]