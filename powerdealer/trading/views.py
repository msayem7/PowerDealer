from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Business
from .serializers import SignupSerializer, LoginSerializer, BusinessSerializer


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            user = data['user']
            business = data['business']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Signup successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'business': BusinessSerializer(business).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                try:
                    business = user.business
                except Business.DoesNotExist:
                    return Response({
                        'error': 'Business not found for this user'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Login successful',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    },
                    'business': BusinessSerializer(business).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                }, status=status.HTTP_200_OK)
            
            return Response({
                'error': 'Invalid username or password'
            }, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessDetailView(APIView):
    def get(self, request):
        """Get current user's business"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'Not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            business = request.user.business
        except Business.DoesNotExist:
            return Response({
                'error': 'Business not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(BusinessSerializer(business).data)

    def put(self, request):
        """Update current user's business"""
        if not request.user.is_authenticated:
            return Response({
                'error': 'Not authenticated'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            business = request.user.business
        except Business.DoesNotExist:
            return Response({
                'error': 'Business not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BusinessSerializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

