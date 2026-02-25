from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.models import Max


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
        validators=[RegexValidator(r"^\d{10}$", "MPRN must be exactly 10 digits.")],
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


class Trade(models.Model):
    """Trade model for monthly trading records per customer"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='trades')
    trade_no = models.PositiveIntegerField(verbose_name='Trade Number')
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    p_therm = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        verbose_name='Price per Thermal Unit',
        validators=[MinValueValidator(0)]
    )
    percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    trade_date = models.DateField(verbose_name='Trade Date')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month', '-trade_no']
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'year', 'month', 'trade_no'],
                name='unique_trade_per_customer_month_year',
            )
        ]

    def __str__(self):
        return f"Trade {self.trade_no} - {self.customer} ({self.month}/{self.year})"

    def save(self, *args, **kwargs):
        if not self.trade_no:
            max_trade = Trade.objects.filter(
                customer=self.customer,
                year=self.year,
                month=self.month
            ).aggregate(Max('trade_no'))['trade_no__max']
            self.trade_no = (max_trade or 0) + 1
        super().save(*args, **kwargs)
