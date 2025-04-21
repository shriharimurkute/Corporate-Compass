from django.contrib import admin
from .models import Agency

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'managed_by', 'address', 'created_at')
    search_fields = ('name', 'managed_by__username')
    list_filter = ('created_at',)