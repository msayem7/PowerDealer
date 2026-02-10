from django.db import models
from django.contrib.auth.models import User


class Business(models.Model):
    """Multi-tenant Business model"""
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business')
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
