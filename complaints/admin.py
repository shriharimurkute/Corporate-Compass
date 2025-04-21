from django.contrib import admin
from .models import Complaint

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('receipt_id', 'user', 'tagged_agency', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'tagged_agency', 'created_at')
    search_fields = ('receipt_id', 'user__username', 'description', 'tagged_agency__name')
    readonly_fields = ('complaint_id', 'receipt_id', 'created_at', 'updated_at', 'response_timestamp')
    fieldsets = (
        (None, {
            'fields': ('complaint_id', 'receipt_id', 'user', 'user_address', 'description', 'image')
        }),
        ('Agency Information', {
            'fields': ('tagged_agency', 'status', 'agency_response', 'response_timestamp')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )