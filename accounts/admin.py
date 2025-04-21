from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    # Add user_type to the display and fieldsets if desired
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'user_type')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'address')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('user_type', 'address')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)