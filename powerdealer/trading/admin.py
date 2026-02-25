from django.contrib import admin
from .models import Business, Customer, Trade


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'email', 'created_at']
    search_fields = ['name', 'email', 'owner__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Owner', {'fields': ('owner',)}),
        ('Business Info', {'fields': ('name', 'email', 'phone', 'description')}),
        ('Address', {'fields': ('address',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'business', 'mobile', 'mprn', 'is_active', 'created_at']
    list_filter = ['is_active', 'business']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'mobile', 'mprn']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User', {'fields': ('user', 'business')}),
        ('Customer Info', {'fields': ('mobile', 'address', 'mprn')}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ['trade_no', 'customer', 'month', 'year', 'p_therm', 'percent', 'trade_date', 'created_at']
    list_filter = ['year', 'month', 'customer__business']
    search_fields = ['customer__user__first_name', 'customer__user__last_name', 'customer__mprn', 'customer__mobile']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-year', '-month', '-trade_no']
    fieldsets = (
        ('Customer', {'fields': ('customer',)}),
        ('Trade Details', {'fields': ('trade_no', 'month', 'year', 'p_therm', 'percent', 'trade_date')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

