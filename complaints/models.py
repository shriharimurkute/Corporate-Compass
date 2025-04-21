from datetime import datetime
import uuid
from django.db import models
from django.conf import settings
from agencies.models import Agency # Import Agency model

class Complaint(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),       # 25%
        ('viewed', 'Viewed by Agency'), # 50%
        ('resolved', 'Resolved'),       # 100%
        ('rejected', 'Rejected'), # Optional other statuses
    )

    complaint_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    receipt_id = models.CharField(max_length=20, unique=True, blank=True, editable=False) # Separate human-readable ID

    # User who submitted the complaint
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # If user is deleted, remove their complaints
        related_name='complaints',
        limit_choices_to={'user_type': 'user'} # Ensure only regular users can file
    )
    # Address related to the specific complaint (might differ from user profile)
    user_address = models.TextField(verbose_name="Location Address of Complaint")
    description = models.TextField()
    image = models.ImageField(upload_to='complaint_images/', blank=True, null=True, verbose_name="Image (Optional)")

    # Mandatory link to the agency being complained about
    tagged_agency = models.ForeignKey(
        Agency,
        on_delete=models.PROTECT, # Prevent deleting agency if complaints are linked
        related_name='tagged_complaints',
        verbose_name="Concerned Agency Department"
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    agency_response = models.TextField(blank=True, null=True, verbose_name="Agency Response")
    response_timestamp = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Tracks edits and status changes

    def save(self, *args, **kwargs):
        if not self.receipt_id:
            # Generate a unique receipt ID (e.g., CC + timestamp + partial UUID)
            timestamp_part = self.created_at.strftime('%Y%m%d%H%M%S') if self.created_at else datetime.now().strftime('%Y%m%d%H%M%S')
            uuid_part = str(self.complaint_id).split('-')[0] # Use first part of UUID
            self.receipt_id = f"CC-{timestamp_part}-{uuid_part.upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Complaint {self.receipt_id} by {self.user.username}"

    def get_status_percentage(self):
        if self.status == 'submitted':
            return 25
        elif self.status == 'viewed':
            return 50
        elif self.status == 'resolved':
            return 100
        # Add other statuses if needed
        return 0 # Default/unknown

    class Meta:
        ordering = ['-created_at'] # Show newest complaints first