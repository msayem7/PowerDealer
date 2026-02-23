from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


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


class Customer(models.Model):
    """Customer profile extending User, scoped to a Business"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='customers')
    mobile = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    mprn = models.CharField(
        max_length=10,
        verbose_name='MPRN',
        validators=[RegexValidator(r'^\d{10}$', 'MPRN must be exactly 10 digits.')],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['business', 'mprn'],
                name='unique_mprn_per_business',
            ),
            models.UniqueConstraint(
                fields=['business', 'mobile'],
                name='unique_mobile_per_business',
            ),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.mprn}"
