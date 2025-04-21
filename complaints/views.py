from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from .models import Complaint
from agencies.models import Agency
from .forms import ComplaintSubmitForm, ComplaintEditForm, ComplaintResponseForm, ComplaintTrackForm
from accounts.views import is_agency_admin # Reuse check function

# --- Helper function to check if user is a regular user ---
def is_regular_user(user):
    return user.is_authenticated and user.user_type == 'user'

# --- Submit Complaint (Regular User Only) ---
@login_required
@user_passes_test(is_regular_user, login_url='/login/')
def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user # Assign logged-in user
            complaint.status = 'submitted' # Initial status
            # complaint.save() will generate receipt_id via the overridden save method
            complaint.save()
            messages.success(request, f"Complaint submitted successfully! Your Receipt ID is: {complaint.receipt_id}")
            return redirect('complaint_receipt', pk=complaint.pk) # Redirect to receipt page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ComplaintSubmitForm()

    agencies = Agency.objects.all() # Pass agencies for dropdown
    return render(request, 'complaints/complaint_form.html', {'form': form, 'agencies': agencies, 'title': 'Submit New Complaint'})

# --- View Complaint Receipt ---
@login_required
def complaint_receipt(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    # Security check: Only owner or relevant agency admin should ideally see receipt directly?
    # Or maybe receipt is public once submitted? Let's allow any logged-in user for now.
    # if complaint.user != request.user and (not is_agency_admin(request.user) or complaint.tagged_agency.managed_by != request.user):
    #     messages.error(request, "You do not have permission to view this receipt.")
    #     return redirect('home')
    return render(request, 'complaints/complaint_receipt.html', {'complaint': complaint})


# --- List All Complaints (Visible to all logged-in users) ---
@login_required
def complaint_list(request):
    # Add pagination later if needed
    complaints = Complaint.objects.all().select_related('user', 'tagged_agency').order_by('-created_at')
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints, 'title': 'All Complaints'})

# --- List My Complaints (Regular User Only) ---
@login_required
@user_passes_test(is_regular_user, login_url='/login/')
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).select_related('tagged_agency').order_by('-created_at')
    return render(request, 'complaints/complaint_list.html', {'complaints': complaints, 'title': 'My Submitted Complaints'})


# --- Complaint Detail View (Visible to all logged-in users) ---
@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint.objects.select_related('user', 'tagged_agency'), pk=pk)
    response_form = None
    can_respond = False
    can_mark_viewed = False

    # Check if logged-in user is the admin for the tagged agency
    if is_agency_admin(request.user):
         # Ensure agency admin user actually has a managing agency profile linked
         if hasattr(request.user, 'managing_agency') and request.user.managing_agency == complaint.tagged_agency:
            can_respond = True
            if complaint.status == 'submitted':
                 can_mark_viewed = True # Only allow marking as viewed if status is 'submitted'

            # Prepare response form if agency hasn't responded yet
            if complaint.status != 'resolved':
                 response_form = ComplaintResponseForm(instance=complaint)


    # Mark as viewed if agency admin views it for the first time
    if can_mark_viewed and complaint.status == 'submitted':
        complaint.status = 'viewed'
        complaint.save(update_fields=['status', 'updated_at'])
        messages.info(request, f"Complaint {complaint.receipt_id} marked as viewed.")
        # Refresh object after save if necessary, though not strictly needed here

    context = {
        'complaint': complaint,
        'response_form': response_form,
        'can_respond': can_respond,
        'can_edit_delete': complaint.user == request.user and complaint.status == 'submitted', # Allow edit/delete only if owner and submitted
        'percentage': complaint.get_status_percentage(),
    }
    return render(request, 'complaints/complaint_detail.html', context)


# --- Edit Complaint (Owner User Only, if status allows) ---
@login_required
@user_passes_test(is_regular_user, login_url='/login/')
def edit_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, user=request.user) # Ensure ownership

    # Optional: Restrict editing based on status (e.g., only if 'submitted')
    if complaint.status != 'submitted':
         messages.error(request, "This complaint cannot be edited as it's already being processed.")
         return redirect('complaint_detail', pk=complaint.pk)

    if request.method == 'POST':
        form = ComplaintEditForm(request.POST, request.FILES, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, "Complaint updated successfully!")
            return redirect('complaint_detail', pk=complaint.pk)
        else:
             messages.error(request, "Please correct the errors below.")
    else:
        form = ComplaintEditForm(instance=complaint)

    return render(request, 'complaints/complaint_form.html', {'form': form, 'title': 'Edit Complaint', 'is_edit': True})


# --- Delete Complaint (Owner User Only, if status allows) ---
@login_required
@user_passes_test(is_regular_user, login_url='/login/')
def delete_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk, user=request.user) # Ensure ownership

    # Optional: Restrict deletion based on status
    if complaint.status != 'submitted':
         messages.error(request, "This complaint cannot be deleted as it's already being processed.")
         return redirect('complaint_detail', pk=complaint.pk)

    if request.method == 'POST':
        receipt_id = complaint.receipt_id # Get id before deleting
        complaint.delete()
        messages.success(request, f"Complaint {receipt_id} deleted successfully.")
        return redirect('my_complaints') # Redirect to user's complaint list

    # If GET request, show a confirmation page (good practice)
    return render(request, 'complaints/complaint_confirm_delete.html', {'complaint': complaint})


# --- Respond to Complaint (Agency Admin Only) ---
@login_required
@user_passes_test(is_agency_admin, login_url='/login/')
def respond_complaint(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)

    # Security Check: Ensure the logged-in user is the admin for *this* complaint's agency
    if not hasattr(request.user, 'managing_agency') or request.user.managing_agency != complaint.tagged_agency:
        messages.error(request, "You do not have permission to respond to this complaint.")
        return redirect('agency_dashboard') # Or complaint list

    if complaint.status == 'resolved':
         messages.warning(request, "This complaint has already been resolved.")
         return redirect('complaint_detail', pk=pk)

    if request.method == 'POST':
        form = ComplaintResponseForm(request.POST, instance=complaint)
        if form.is_valid():
            response_instance = form.save(commit=False)
            response_instance.status = 'resolved' # Update status to resolved
            response_instance.response_timestamp = timezone.now() # Record time of response
            response_instance.save(update_fields=['agency_response', 'status', 'response_timestamp', 'updated_at'])
            messages.success(request, f"Response submitted for complaint {complaint.receipt_id}.")
            return redirect('complaint_detail', pk=pk)
        else:
             messages.error(request, "Could not submit response. Please check the form.")
             # Re-render detail page with the invalid form (will show errors)
             context = {
                'complaint': complaint,
                'response_form': form, # Pass the invalid form back
                'can_respond': True,
                'percentage': complaint.get_status_percentage(),
              }
             return render(request, 'complaints/complaint_detail.html', context)
    else:
         # Should not happen if response form is only shown on detail page POST, but handle just in case
         messages.error(request, "Invalid request method for responding.")
         return redirect('complaint_detail', pk=pk)

# --- Track Complaint Page ---
def track_complaint_status(request):
    complaint = None
    form = ComplaintTrackForm()
    if request.method == 'GET' and 'receipt_id' in request.GET:
        form = ComplaintTrackForm(request.GET)
        if form.is_valid():
            receipt_id = form.cleaned_data['receipt_id']
            try:
                complaint = Complaint.objects.select_related('user', 'tagged_agency').get(receipt_id__iexact=receipt_id) # Case-insensitive search
            except Complaint.DoesNotExist:
                messages.error(request, f"Complaint with Receipt ID '{receipt_id}' not found.")
            except Complaint.MultipleObjectsReturned:
                 messages.error(request, f"Error: Multiple complaints found for ID '{receipt_id}'. Please contact support.")


    context = {
        'form': form,
        'complaint': complaint,
        'percentage': complaint.get_status_percentage() if complaint else 0,
    }
    return render(request, 'complaints/track_complaint.html', context)