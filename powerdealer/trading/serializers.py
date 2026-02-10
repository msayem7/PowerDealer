from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Business


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
