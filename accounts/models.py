# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('user', 'Regular User'),
        ('agency', 'Agency Admin'),
    )
    # Add additional fields if needed, inherit standard fields
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='user')
    # Add address field for regular users if needed for profile, else get from complaint
    address = models.TextField(blank=True, null=True) # Optional profile address

    def __str__(self):
        return self.username

    # Add related_name to avoid clashes with default User model groups/permissions
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name="customuser_set",
        related_query_name="user",
    )