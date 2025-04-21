from django import forms
from .models import Complaint
from agencies.models import Agency

class ComplaintSubmitForm(forms.ModelForm):
    # Ensure agency dropdown is populated
    tagged_agency = forms.ModelChoiceField(
        queryset=Agency.objects.all().order_by('name'),
        empty_label="-- Select Agency Department --",
        widget=forms.Select(attrs={'class': 'form-control'}) # Add some styling if using Bootstrap
    )

    class Meta:
        model = Complaint
        fields = ['user_address', 'description', 'image', 'tagged_agency']
        widgets = {
            'user_address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter the full address where the issue occurred'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Describe the problem in detail'}),
        }

class ComplaintEditForm(forms.ModelForm):
    # Allow editing description and image, maybe address. Cannot change user or agency easily.
     class Meta:
        model = Complaint
        fields = ['user_address', 'description', 'image'] # Fields user can edit
        widgets = {
            'user_address': forms.Textarea(attrs={'rows': 3}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }

class ComplaintResponseForm(forms.ModelForm):
    # Form for agency admin to respond
    class Meta:
        model = Complaint
        fields = ['agency_response']
        widgets = {
            'agency_response': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter your official response or action taken.'}),
        }

class ComplaintTrackForm(forms.Form):
    receipt_id = forms.CharField(max_length=50, label="Enter Complaint Receipt ID")