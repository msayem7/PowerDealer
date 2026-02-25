import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import connection

from .models import Business, Customer, Trade
from .serializers import (
    SignupSerializer, LoginSerializer, BusinessSerializer,
    CustomerSerializer, CustomerCreateSerializer, TradeSerializer,
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


class TradeListCreateView(APIView):
    """List and create trades for the authenticated business."""

    def _get_business(self, request):
        """Helper to get business for authenticated user."""
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
        return business, None

    def get(self, request):
        """List all trades for the business with optional filtering."""
        business, error_response = self._get_business(request)
        if error_response:
            return error_response

        # Start with trades for customers in this business
        trades = Trade.objects.filter(customer__business=business).select_related('customer__user')

        # Apply filters
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            trades = trades.filter(customer_id=customer_id)

        month = request.query_params.get('month')
        if month:
            trades = trades.filter(month=int(month))

        year = request.query_params.get('year')
        if year:
            trades = trades.filter(year=int(year))

        # Order by trade_no within each customer/month/year
        trades = trades.order_by('year', 'month', 'trade_no')

        serializer = TradeSerializer(trades, many=True)
        return Response({
            'success': True,
            'message': 'Trades retrieved successfully.',
            'data': serializer.data,
        })

    def post(self, request):
        """Create a new trade."""
        business, error_response = self._get_business(request)
        if error_response:
            return error_response

        serializer = TradeSerializer(data=request.data)
        if serializer.is_valid():
            # Verify customer belongs to this business
            customer = serializer.validated_data.get('customer')
            if customer.business_id != business.id:
                return Response({
                    'success': False,
                    'message': 'Customer does not belong to your business.',
                    'errors': {}
                }, status=status.HTTP_400_BAD_REQUEST)

            trade = serializer.save()
            logger.info(f"Trade created: {trade.trade_no} for customer {customer.mprn}")
            return Response({
                'success': True,
                'message': 'Trade created successfully.',
                'data': TradeSerializer(trade).data,
            }, status=status.HTTP_201_CREATED)

        logger.warning(f"Trade creation failed: {serializer.errors}")
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class TradeDetailView(APIView):
    """Retrieve, update, and delete a single trade."""

    def _get_trade(self, request, trade_id):
        """Helper to authenticate, scope to business, and fetch trade."""
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
            trade = Trade.objects.select_related('customer__user').get(
                id=trade_id,
                customer__business=business
            )
        except Trade.DoesNotExist:
            return None, Response({
                'success': False,
                'message': 'Trade not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        return trade, None

    def get(self, request, trade_id):
        """Retrieve a single trade."""
        trade, error_response = self._get_trade(request, trade_id)
        if error_response:
            return error_response
        return Response({
            'success': True,
            'message': 'Trade retrieved successfully.',
            'data': TradeSerializer(trade).data,
        })

    def put(self, request, trade_id):
        """Update a trade (full update)."""
        trade, error_response = self._get_trade(request, trade_id)
        if error_response:
            return error_response

        serializer = TradeSerializer(trade, data=request.data)
        if serializer.is_valid():
            trade = serializer.save()
            logger.info(f"Trade updated: {trade.id}")
            return Response({
                'success': True,
                'message': 'Trade updated successfully.',
                'data': TradeSerializer(trade).data,
            })
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, trade_id):
        """Update a trade (partial update)."""
        trade, error_response = self._get_trade(request, trade_id)
        if error_response:
            return error_response

        serializer = TradeSerializer(trade, data=request.data, partial=True)
        if serializer.is_valid():
            trade = serializer.save()
            logger.info(f"Trade updated: {trade.id}")
            return Response({
                'success': True,
                'message': 'Trade updated successfully.',
                'data': TradeSerializer(trade).data,
            })
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, trade_id):
        """Delete a trade."""
        trade, error_response = self._get_trade(request, trade_id)
        if error_response:
            return error_response

        trade_id_display = trade.id
        trade.delete()
        logger.info(f"Trade deleted: {trade_id_display}")
        return Response({
            'success': True,
            'message': 'Trade deleted successfully.',
        })


class TradingPivotView(APIView):
    """Get trading data in pivot format for a customer for a full year."""

    def _get_business(self, request):
        """Helper to get business for authenticated user."""
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
        return business, None

    def get(self, request):
        """Get pivot data for a customer for a year.
        
        Query params:
        - mprn: Required - MPRN of the customer (10 digits)
        - OR customer_id: Required - ID of the customer
        - year: Required - Year to get data for
        """
        import calendar

        business, error_response = self._get_business(request)
        if error_response:
            return error_response

        # Support both mprn and customer_id parameters
        mprn = request.query_params.get('mprn')
        customer_id = request.query_params.get('customer_id')
        year = request.query_params.get('year')

        if not year:
            return Response({
                'success': False,
                'message': 'year is required.',
                'errors': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            year = int(year)
        except ValueError:
            return Response({
                'success': False,
                'message': 'year must be an integer.',
                'errors': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find customer by MPRN or customer_id
        customer = None
        if mprn:
            try:
                customer = Customer.objects.get(mprn=mprn, business=business)
            except Customer.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Customer not found with this MPRN.',
                    'errors': {}
                }, status=status.HTTP_404_NOT_FOUND)
        elif customer_id:
            try:
                customer_id = int(customer_id)
                customer = Customer.objects.get(id=customer_id, business=business)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'customer_id must be an integer.',
                    'errors': {}
                }, status=status.HTTP_400_BAD_REQUEST)
            except Customer.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Customer not found.',
                    'errors': {}
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({
                'success': False,
                'message': 'Either mprn or customer_id is required.',
                'errors': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get all trades for this customer/year
        trades = Trade.objects.filter(
            customer=customer,
            year=year
        ).order_by('month', 'trade_no')

        # Group trades by month
        trades_by_month = {}
        for trade in trades:
            if trade.month not in trades_by_month:
                trades_by_month[trade.month] = []
            trades_by_month[trade.month].append(TradeSerializer(trade).data)

        # Build pivot response (12 months)
        pivot_data = []
        for month_num in range(1, 13):
            month_trades = trades_by_month.get(month_num, [])
            
            # Calculate total_percent (TB - Total Booked)
            # Convert to float to handle DecimalField serialization (DRF serializes as string)
            total_percent = sum(float(t['percent']) for t in month_trades)
            
            # Calculate average_price_achieved (AP - Average Price)
            # Weighted average = Σ(P/Therm_i × Percent_i) / Σ(Percent_i)
            if total_percent > 0:
                weighted_sum = sum((float(t['p_therm']) * float(t['percent'])) for t in month_trades)
                average_price_achieved = round(weighted_sum / total_percent, 4)
            else:
                average_price_achieved = 0

            pivot_data.append({
                'month': month_num,
                'month_name': calendar.month_name[month_num],
                'trades': month_trades,
                'total_percent': total_percent,
                'average_price_achieved': average_price_achieved,
            })

        return Response({
            'success': True,
            'message': 'Pivot data retrieved successfully.',
            'data': {
                'customer_id': customer.id,
                'customer_mprn': customer.mprn,
                'customer_name': customer.user.get_full_name() or customer.user.username,
                'year': year,
                'months': pivot_data,
            },
        })

