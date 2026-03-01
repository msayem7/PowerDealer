from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Business, Customer, Trade


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class BusinessSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Business
        fields = ['id', 'owner', 'name', 'description', 'email', 'phone', 'address', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'created_at', 'updated_at']


class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    business_name = serializers.CharField(max_length=255)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_business_name(self, value):
        if Business.objects.filter(name=value).exists():
            raise serializers.ValidationError("Business name already exists.")
        return value

    def create(self, validated_data):
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Create business with default values for removed fields
        business = Business.objects.create(
            owner=user,
            name=validated_data['business_name'],
            email=validated_data['email'],  # Use user's email as business email
            phone='',  # Removed from signup
            description=''  # Removed from signup
        )

        return {'user': user, 'business': business}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer read/update operations. id is never exposed."""
    user = UserSerializer(read_only=True)
    name = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'user', 'mobile', 'address', 'mprn', 'is_active',
            'name', 'email', 'created_at', 'updated_at',
        ]
        read_only_fields = ['business', 'created_at', 'updated_at']

    def validate_mprn(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("MPRN must be exactly 10 digits.")
        business = self.instance.business if self.instance else self.context.get('business')
        if business:
            qs = Customer.objects.filter(business=business, mprn=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("This MPRN is already registered in your business.")
        return value

    def validate_mobile(self, value):
        # Skip validation if mobile is empty (now optional)
        if not value:
            return value
        business = self.instance.business if self.instance else self.context.get('business')
        if business:
            qs = Customer.objects.filter(business=business, mobile=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("This mobile number is already registered in your business.")
        return value

    def validate_email(self, value):
        if value:
            qs = User.objects.filter(email=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.user.pk)
            if qs.exists():
                raise serializers.ValidationError("This email is already registered.")
        return value

    def update(self, instance, validated_data):
        # Extract user fields
        name = validated_data.pop('name', None)
        email = validated_data.pop('email', None)

        # Update User fields
        user = instance.user
        if name is not None:
            user.first_name = name  # Store full name in first_name
        if email is not None:
            user.email = email
        user.save()

        # Update Customer fields
        return super().update(instance, validated_data)


class CustomerCreateSerializer(serializers.Serializer):
    """Serializer for creating a new Customer + User atomically."""
    name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    mobile = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    mprn = serializers.CharField(max_length=10)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_mobile(self, value):
        if not value:  # Skip validation if mobile is empty
            return value
        business = self.context.get('business')
        if business and Customer.objects.filter(business=business, mobile=value).exists():
            raise serializers.ValidationError("This mobile number is already registered in your business.")
        return value

    def validate_mprn(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("MPRN must be exactly 10 digits.")
        business = self.context.get('business')
        if business and Customer.objects.filter(business=business, mprn=value).exists():
            raise serializers.ValidationError("This MPRN is already registered in your business.")
        return value

    def create(self, validated_data):
        from django.db import transaction

        business = self.context['business']

        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['name'],  # Store full name in first_name
                last_name='',
            )
            customer = Customer.objects.create(
                user=user,
                business=business,
                mobile=validated_data.get('mobile', ''),
                address=validated_data.get('address', ''),
                mprn=validated_data['mprn'],
            )
        return customer


class CustomerNestedSerializer(serializers.ModelSerializer):
    """Nested serializer for customer details (MPRN, name)"""
    name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'mprn', 'name', 'email', 'mobile']

    def get_name(self, obj):
        # Get full name from user - first_name now contains the full customer name
        full_name = obj.user.get_full_name()
        return full_name if full_name else obj.user.username


class TradeSerializer(serializers.ModelSerializer):
    """Serializer for Trade model with nested customer details"""
    customer = CustomerNestedSerializer(read_only=True)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True,
        required=False
    )
    # Allow using mprn instead of customer_id for creating trades
    mprn = serializers.CharField(write_only=True, required=False)
    month_name = serializers.SerializerMethodField()

    class Meta:
        model = Trade
        fields = [
            'id', 'customer', 'customer_id', 'mprn', 'trade_no', 'month', 'month_name',
            'year', 'p_therm', 'percent', 'trade_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['trade_no', 'created_at', 'updated_at']

    def get_month_name(self, obj):
        import calendar
        return calendar.month_name[obj.month]

    def validate(self, attrs):
        # For partial updates, use instance values for missing fields
        if self.instance:
            # Get values from instance if not provided in attrs
            if 'customer' not in attrs:
                attrs['customer'] = self.instance.customer
            if 'month' not in attrs:
                attrs['month'] = self.instance.month
            if 'year' not in attrs:
                attrs['year'] = self.instance.year
        
        # If mprn is provided, look up the customer within the user's business
        mprn = attrs.pop('mprn', None)
        if mprn and not attrs.get('customer'):
            # Get the business from the request user
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                try:
                    business = request.user.business
                    customer = Customer.objects.get(mprn=mprn, business=business)
                    attrs['customer'] = customer
                except Customer.DoesNotExist:
                    raise serializers.ValidationError({'mprn': 'Customer with this MPRN not found in your business.'})
                except Customer.MultipleObjectsReturned:
                    raise serializers.ValidationError({'mprn': 'Multiple customers found with this MPRN. Please contact support.'})
            else:
                raise serializers.ValidationError({'mprn': 'Authentication required to look up customer by MPRN.'})
        
        # Validate that customer is provided (only for create, not partial update)
        if not attrs.get('customer') and not self.instance:
            raise serializers.ValidationError({'customer_id': 'Either customer_id or mprn is required.'})
        
        # Validate percent
        customer = attrs.get('customer')
        month = attrs.get('month')
        year = attrs.get('year')
        percent = attrs.get('percent', 0)

        if customer and month and year:
            # Get existing trades for this customer/month/year
            queryset = Trade.objects.filter(
                customer=customer,
                month=month,
                year=year
            )

            # Exclude current instance if updating
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            total_percent = sum(t.percent for t in queryset)
            new_total = total_percent + percent

            if new_total > 100:
                raise serializers.ValidationError({
                    'percent': f"Total booked ({new_total}%) would exceed 100%. Current total: {total_percent}%"
                })

        return attrs

    def create(self, validated_data):
        """Create trade - trade_no is auto-generated in model's save method"""
        return super().create(validated_data)
