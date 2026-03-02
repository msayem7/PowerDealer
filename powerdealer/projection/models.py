from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from decimal import Decimal
from trading.models import Customer, Trade
import calendar


class CostProjection(models.Model):
    """Cost projection model for monthly gas cost calculations per customer"""
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='cost_projections'
    )
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)]
    )
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    st_charge = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Standing Charge (p/day)',
        validators=[MinValueValidator(0)]
    )
    consumption = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Consumption (kWh)',
        validators=[MinValueValidator(0)]
    )
    flex_rate = models.DecimalField(
        max_digits=12,
        decimal_places=8,
        default=0,
        verbose_name='Flex Unit Rate (p/kWh)',
        validators=[MinValueValidator(0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        constraints = [
            models.UniqueConstraint(
                fields=['customer', 'year', 'month'],
                name='unique_projection_per_customer_month_year',
            )
        ]

    def __str__(self):
        return f"Cost.customer.mprnProjection - {self} ({self.month}/{self.year})"

    @property
    def traded_price(self):
        """Calculate weighted average traded price from Trade model dynamically.
        
        Formula: Weighted Average = SUM(p_therm × percent) / SUM(percent)
        
        Returns:
            Decimal: Weighted average traded price in p/therm (8 decimal places)
        """
        trades = Trade.objects.filter(
            customer=self.customer,
            year=self.year,
            month=self.month
        )
        
        total_weighted_price = sum(t.p_therm * t.percent for t in trades)
        total_percent = sum(t.percent for t in trades)
        
        if total_percent > 0:
            return round(total_weighted_price / total_percent, 8)
        return Decimal('0')

    @property
    def cost(self):
        """Calculate monthly cost dynamically.
        
        Cost (£) = (St Charge p/day × No of Days / 100) + 
                   (Consumption (kWh) × (Flex Unit Rate + Traded Price / 29.3071) / 100)
        
        Returns:
            Decimal: Monthly cost in pounds (2 decimal places)
        """
        # Get number of days in the month for the given year
        no_of_days = calendar.monthrange(self.year, self.month)[1]
        
        # Get traded price dynamically
        tp = self.traded_price
        
        # Convert pence to pounds
        # Standing charge component: (p/day × days) / 100
        st_charge_component = Decimal(self.st_charge) * Decimal(self.no_of_days) / Decimal('100')
        
        # Unit consumption component: (kWh × (flex_rate + traded_price/29.3071)) / 100
        traded_price_per_kwh = tp / Decimal('29.3071')
        unit_component = (Decimal(self.consumption) * (Decimal(self.flex_rate) + Decimal(traded_price_per_kwh))) / Decimal('100')
        
        total_cost = Decimal(st_charge_component) + Decimal(unit_component)
        return round(total_cost, 2)

    @property
    def no_of_days(self):
        """Get number of days in the month for the given year.
        
        Returns:
            int: Number of days (handles leap years)
        """
        return calendar.monthrange(self.year, self.month)[1]
