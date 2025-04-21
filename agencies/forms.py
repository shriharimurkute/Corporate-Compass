from django import forms
from .models import Agency

class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ['name', 'address', 'logo', 'tagline']
        # Exclude 'managed_by' as it will be set automatically in the view