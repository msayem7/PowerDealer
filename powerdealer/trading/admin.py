from django.contrib import admin
from .models import Business


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

