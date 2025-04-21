from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserRegisterForm(UserCreationForm):
    # Add any extra fields needed during user registration
    address = forms.CharField(widget=forms.Textarea, required=False)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'address') # Add fields here

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'user' # Explicitly set type
        user.address = self.cleaned_data['address']
        if commit:
            user.save()
        return user

class AgencyAdminRegisterForm(UserCreationForm):
    # Agency specific fields if any during user creation itself
    # Usually agency details are added separately after admin logs in
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name') # Keep it simple

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'agency' # Explicitly set type
        if commit:
            user.save()
        return user

class CustomLoginForm(AuthenticationForm):
    # Inherit standard login form
    pass