from django.contrib import admin
from .models import CostProjection


@admin.register(CostProjection)
class CostProjectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'year', 'month', 'st_charge', 'consumption', 
                    'flex_rate', 'traded_price', 'cost', 'created_at']
    list_filter = ['year', 'month', 'customer__business']
    search_fields = ['customer__user__first_name', 'customer__user__last_name', 
                     'customer__mprn', 'customer__mobile']
    readonly_fields = ['traded_price', 'cost', 'created_at', 'updated_at']
    ordering = ['-year', '-month', 'customer']
    fieldsets = (
        ('Customer', {'fields': ('customer',)}),
        ('Period', {'fields': ('year', 'month')}),
        ('Input Values', {'fields': ('st_charge', 'consumption', 'flex_rate')}),
        ('Calculated Values', {'fields': ('traded_price', 'cost')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
