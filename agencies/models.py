from django.db import models
from django.conf import settings # To link to CustomUser

class Agency(models.Model):
    # Link to the agency admin user who manages/registered this agency
    # OneToOneField implies one admin user manages exactly one agency profile.
    # Use ForeignKey if one admin could potentially register multiple distinct agencies.
    # Let's assume OneToOne for simplicity as requested initially.
    managed_by = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # If admin user is deleted, delete agency profile
        related_name='managing_agency',
        limit_choices_to={'user_type': 'agency'} # Ensure only agency admins can be linked
    )
    name = models.CharField(max_length=200, unique=True, verbose_name="Department Name")
    address = models.TextField()
    logo = models.ImageField(upload_to='agency_logos/', blank=True, null=True)
    tagline = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Agency"
        verbose_name_plural = "Agencies"