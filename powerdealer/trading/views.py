import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import connection

from .models import Business, Customer
from .serializers import (
    SignupSerializer, LoginSerializer, BusinessSerializer,
    CustomerSerializer, CustomerCreateSerializer,
)

logger = logging.getLogger(__name__)


class HealthCheckView(APIView):
    """Health check endpoint for container orchestration"""
    def get(self, request):
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            db_status = "healthy"
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"
            logger.error(f"Health check failed: {e}")
            return Response({
                "status": "unhealthy",
                "database": db_status
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({
            "status": "healthy",
            "database": db_status
        })


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


class CustomerListCreateView(APIView):
    """List and create customers for the authenticated business owner."""

    def get(self, request):
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

        customers = Customer.objects.filter(business=business).select_related('user')
        serializer = CustomerSerializer(customers, many=True)
        return Response({
            'success': True,
            'message': 'Customers retrieved successfully.',
            'data': serializer.data,
        })

    def post(self, request):
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

        serializer = CustomerCreateSerializer(data=request.data, context={'business': business})
        if serializer.is_valid():
            customer = serializer.save()
            logger.info(f"Customer created: {customer.user.email} for business {business.name}")
            return Response({
                'success': True,
                'message': 'Customer created successfully.',
                'data': CustomerSerializer(customer).data,
            }, status=status.HTTP_201_CREATED)

        logger.warning(f"Customer creation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailView(APIView):
    """Retrieve and update a single customer by MPRN, scoped to business."""

    def _get_customer(self, request, mprn):
        """Helper to authenticate, scope to business, and fetch customer by MPRN."""
        if not request.user.is_authenticated:
            return None, Response({
                'success': False,
                'message': 'Login required.',
                'errors': {}
            }, status=status.HTTP_401_UNAUTHORIZED)
        try:
            business = request.user.business
        except Business.DoesNotExist:
            return None, Response({
                'success': False,
                'message': 'Business not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        try:
            customer = Customer.objects.select_related('user').get(mprn=mprn, business=business)
        except Customer.DoesNotExist:
            return None, Response({
                'success': False,
                'message': 'Customer not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        return customer, None

    def get(self, request, mprn):
        customer, error_response = self._get_customer(request, mprn)
        if error_response:
            return error_response
        return Response({
            'success': True,
            'message': 'Customer retrieved successfully.',
            'data': CustomerSerializer(customer).data,
        })

    def put(self, request, mprn):
        customer, error_response = self._get_customer(request, mprn)
        if error_response:
            return error_response
        serializer = CustomerSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Customer updated: {customer.user.email}")
            return Response({
                'success': True,
                'message': 'Customer updated successfully.',
                'data': serializer.data,
            })
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, mprn):
        return self.put(request, mprn)

