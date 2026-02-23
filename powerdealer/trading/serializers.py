from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Business, Customer


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
    business_email = serializers.EmailField()
    business_phone = serializers.CharField(max_length=20, required=False)
    description = serializers.CharField(required=False, allow_blank=True)

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

        # Create business
        business = Business.objects.create(
            owner=user,
            name=validated_data['business_name'],
            email=validated_data['business_email'],
            phone=validated_data.get('business_phone', ''),
            description=validated_data.get('description', '')
        )

        return {'user': user, 'business': business}


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer read/update operations. id is never exposed."""
    user = UserSerializer(read_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    email = serializers.EmailField(write_only=True, required=False)

    class Meta:
        model = Customer
        fields = [
            'user', 'mobile', 'address', 'mprn', 'is_active',
            'first_name', 'last_name', 'email', 'created_at', 'updated_at',
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
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        email = validated_data.pop('email', None)

        # Update User fields
        user = instance.user
        if first_name is not None:
            user.first_name = first_name
        if last_name is not None:
            user.last_name = last_name
        if email is not None:
            user.email = email
        user.save()

        # Update Customer fields
        return super().update(instance, validated_data)


class CustomerCreateSerializer(serializers.Serializer):
    """Serializer for creating a new Customer + User atomically."""
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    mobile = serializers.CharField(max_length=20)
    address = serializers.CharField(required=False, allow_blank=True)
    mprn = serializers.CharField(max_length=10)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_mobile(self, value):
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
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
            )
            customer = Customer.objects.create(
                user=user,
                business=business,
                mobile=validated_data['mobile'],
                address=validated_data.get('address', ''),
                mprn=validated_data['mprn'],
            )
        return customer
