from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib import messages
from .forms import UserRegisterForm, AgencyAdminRegisterForm, CustomLoginForm
from .models import CustomUser
from agencies.models import Agency # Import Agency model


# ADD THIS FUNCTION DEFINITION HERE:
# ++++++++++++++++++++++++++++++++++++++++++++
def is_agency_admin(user):
    """Checks if a user is authenticated and has the 'agency' user_type."""
    return user.is_authenticated and user.user_type == 'agency'
# ++++++++++++++++++++++++++++++++++++++++++++


# --- Registration Views ---
class UserRegisterView(CreateView):
    model = CustomUser
    form_class = UserRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login') # Redirect to login after registration

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'user'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"User account created for {user.username}. Please log in.")
        # login(self.request, user) # Optionally log in directly
        return redirect(self.success_url)

class AgencyAdminRegisterView(CreateView):
    model = CustomUser
    form_class = AgencyAdminRegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login') # Redirect to login

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'agency'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, f"Agency Admin account created for {user.username}. Please log in.")
        # login(self.request, user) # Optionally log in directly
        return redirect(self.success_url)

# --- Login/Logout Views ---
def login_view(request):
    if request.user.is_authenticated:
         return redirect('dashboard_redirect') # Already logged in

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                # Redirect based on user type
                if user.user_type == 'agency':
                    # Check if agency profile exists
                    if hasattr(user, 'managing_agency') and user.managing_agency:
                         return redirect('agency_dashboard')
                    else:
                         # Redirect to create agency profile first
                         messages.info(request, "Please register your agency details.")
                         return redirect('agency_register')
                else:
                    return redirect('user_dashboard') # Or home/complaint list
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = CustomLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('home') # Redirect to home page after logout

# --- Dashboard Redirector ---
@login_required
def dashboard_redirect_view(request):
    if request.user.user_type == 'agency':
        # Check if agency profile exists before redirecting to dashboard
        if hasattr(request.user, 'managing_agency') and request.user.managing_agency:
            return redirect('agency_dashboard')
        else:
            messages.info(request, "Please register your agency details first.")
            return redirect('agency_register')
    elif request.user.user_type == 'user':
        return redirect('user_dashboard') # Or 'complaint_list' or 'my_complaints'
    else:
        # Fallback or handle unexpected type
        return redirect('home')

# --- User Dashboard (Example) ---
@login_required
def user_dashboard(request):
    if request.user.user_type != 'user':
        messages.warning(request, "Access restricted to regular users.")
        return redirect('home') # Make sure 'home' is a valid URL name
    context = {}
    # Use the namespaced path if the template is in accounts/templates/accounts/
    return render(request, 'accounts/user_dashboard.html', context)
    # If the template is directly in project templates/ or accounts/templates/
    # then 'user_dashboard.html' is correct.