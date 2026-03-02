from rest_framework import serializers
from django.db.models import Sum
from .models import CostProjection
from trading.models import Customer, Trade
import calendar


class CostProjectionSerializer(serializers.ModelSerializer):
    """Serializer for CostProjection model"""
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True
    )
    mprn = serializers.CharField(source='customer.mprn', read_only=True)
    month_name = serializers.SerializerMethodField()
    no_of_days = serializers.SerializerMethodField()

    class Meta:
        model = CostProjection
        fields = [
            'id', 'customer', 'customer_id', 'mprn', 'year', 'month', 'month_name',
            'no_of_days', 'st_charge', 'consumption', 'flex_rate', 
            'traded_price', 'cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['traded_price', 'cost', 'created_at', 'updated_at']

    def get_month_name(self, obj):
        return calendar.month_name[obj.month]

    def get_no_of_days(self, obj):
        return calendar.monthrange(obj.year, obj.month)[1]

    def validate_st_charge(self, value):
        if value < 0:
            raise serializers.ValidationError("Standing charge cannot be negative.")
        return round(value, 2)

    def validate_consumption(self, value):
        if value < 0:
            raise serializers.ValidationError("Consumption cannot be negative.")
        return value

    def validate_flex_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Flex unit rate cannot be negative.")
        return round(value, 8)


class CostProjectionBulkSerializer(serializers.Serializer):
    """Serializer for bulk save of 12-month projections"""
    mprn = serializers.CharField(max_length=10)
    year = serializers.IntegerField()
    projections = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=20, decimal_places=8)
        )
    )

    def validate_mprn(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("MPRN must be exactly 10 digits.")
        return value

    def validate_projections(self, value):
        if len(value) != 12:
            raise serializers.ValidationError("Exactly 12 months required.")
        return value


class ProjectionRowSerializer(serializers.Serializer):
    """Serializer for individual projection row in the grid"""
    month = serializers.IntegerField(min_value=1, max_value=12)
    no_of_days = serializers.IntegerField(read_only=True)
    st_charge = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    consumption = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
    flex_rate = serializers.DecimalField(max_digits=12, decimal_places=8, min_value=0)
    traded_price = serializers.DecimalField(max_digits=12, decimal_places=8, read_only=True)
    cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    def validate_st_charge(self, value):
        if value < 0:
            raise serializers.ValidationError("Standing charge cannot be negative.")
        return round(value, 2)

    def validate_flex_rate(self, value):
        if value < 0:
            raise serializers.ValidationError("Flex unit rate cannot be negative.")
        return round(value, 8)


class ProjectionResponseSerializer(serializers.Serializer):
    """Serializer for the projection API response"""
    mprn = serializers.CharField()
    year = serializers.IntegerField()
    rows = ProjectionRowSerializer(many=True)
