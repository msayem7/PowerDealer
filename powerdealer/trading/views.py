import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from .models import Business
from .serializers import SignupSerializer, LoginSerializer, BusinessSerializer

logger = logging.getLogger(__name__)


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.save()
            user = data['user']
            business = data['business']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            logger.info(f"User signup successful: {user.username}")
            
            return Response({
                'success': True,
                'message': 'Signup successful',
                'data': {
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
                }
            }, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Signup validation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


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
                    logger.warning(f"Login failed - no business found: {username}")
                    return Response({
                        'success': False,
                        'message': 'Business not found for this user.',
                        'errors': {}
                    }, status=status.HTTP_404_NOT_FOUND)
                
                refresh = RefreshToken.for_user(user)
                
                logger.info(f"User login successful: {username}")
                
                return Response({
                    'success': True,
                    'message': 'Login successful',
                    'data': {
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
                    }
                }, status=status.HTTP_200_OK)
            
            logger.warning(f"Login failed - invalid credentials: {username}")
            return Response({
                'success': False,
                'message': 'Invalid username or password.',
                'errors': {}
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """Get current authenticated user and their business"""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Login required.',
                'errors': {}
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        try:
            business = user.business
            business_data = BusinessSerializer(business).data
        except Business.DoesNotExist:
            business_data = None
        
        return Response({
            'success': True,
            'message': 'User retrieved successfully.',
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'business': business_data
            }
        })


class BusinessDetailView(APIView):
    def get(self, request):
        """Get current user's business"""
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Login required.',
                'errors': {}
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            business = request.user.business
        except Business.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Business not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': 'Business retrieved successfully.',
            'data': BusinessSerializer(business).data
        })

    def put(self, request):
        """Update current user's business"""
        if not request.user.is_authenticated:
            return Response({
                'success': False,
                'message': 'Login required.',
                'errors': {}
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            business = request.user.business
        except Business.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Business not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BusinessSerializer(business, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Business updated: {business.name}")
            return Response({
                'success': True,
                'message': 'Business updated successfully.',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

