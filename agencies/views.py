from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Agency
from .forms import AgencyForm
from complaints.models import Complaint # To show related complaints

# --- Helper function to check if user is agency admin ---
def is_agency_admin(user):
    return user.is_authenticated and user.user_type == 'agency'

# --- Agency Registration (by logged-in agency admin) ---
@login_required
@user_passes_test(is_agency_admin, login_url='/login/') # Redirect if not agency admin
def register_agency(request):
    # Check if this admin already manages an agency
    if Agency.objects.filter(managed_by=request.user).exists():
        messages.warning(request, "You have already registered an agency.")
        return redirect('agency_dashboard') # Or agency detail page

    if request.method == 'POST':
        form = AgencyForm(request.POST, request.FILES)
        if form.is_valid():
            agency = form.save(commit=False)
            agency.managed_by = request.user # Assign the logged-in admin
            agency.save()
            messages.success(request, f"Agency '{agency.name}' registered successfully!")
            return redirect('agency_dashboard') # Redirect to agency dashboard
        else:
             messages.error(request, "Please correct the errors below.")
    else:
        form = AgencyForm()

    return render(request, 'agencies/agency_form.html', {'form': form, 'title': 'Register Your Agency'})

# --- Agency List (Visible to all logged-in users) ---
@login_required
def agency_list(request):
    agencies = Agency.objects.all().order_by('name')
    return render(request, 'agencies/agency_list.html', {'agencies': agencies})

# --- Agency Detail (Visible to all logged-in users) ---
@login_required
def agency_detail(request, pk):
    agency = get_object_or_404(Agency, pk=pk)
    # Optionally, show complaints tagged to this agency
    related_complaints = Complaint.objects.filter(tagged_agency=agency).order_by('-created_at')[:10] # Show recent 10
    context = {
        'agency': agency,
        'related_complaints': related_complaints
    }
    return render(request, 'agencies/agency_detail.html', context)

# --- Agency Dashboard (For the logged-in agency admin) ---
@login_required
@user_passes_test(is_agency_admin, login_url='/login/')
def agency_dashboard(request):
    try:
        # Get the agency managed by the current logged-in admin user
        agency = Agency.objects.get(managed_by=request.user)
    except Agency.DoesNotExist:
        # This case should ideally be handled by the redirect in login/dashboard_redirect
        # but is good practice to have a fallback.
        messages.error(request, "Agency profile not found. Please register your agency.")
        return redirect('agency_register')

    # Get complaints tagged to this specific agency
    complaints_for_agency = Complaint.objects.filter(tagged_agency=agency).order_by('-created_at')

    context = {
        'agency': agency,
        'complaints': complaints_for_agency,
        'unresponded_count': complaints_for_agency.filter(status__in=['submitted', 'viewed']).count(),
        'resolved_count': complaints_for_agency.filter(status='resolved').count(),
    }
    return render(request, 'agencies/agency_dashboard.html', context)

# Add views for editing/deleting agency if needed (maybe by superadmin or agency admin themselves)