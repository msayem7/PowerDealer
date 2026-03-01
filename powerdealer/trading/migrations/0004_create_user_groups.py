from django.contrib.auth.models import Group
from django.db import migrations


def create_groups(apps, schema_editor):
    """Create Administrator and Customer groups if they don't exist."""
    Group.objects.get_or_create(name='Administrator')
    Group.objects.get_or_create(name='Customer')


def remove_groups(apps, schema_editor):
    """Remove Administrator and Customer groups."""
    Group.objects.filter(name__in=['Administrator', 'Customer']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0003_trade_trade_unique_trade_per_customer_month_year'),
    ]

    operations = [
        migrations.RunPython(create_groups, remove_groups),
    ]
