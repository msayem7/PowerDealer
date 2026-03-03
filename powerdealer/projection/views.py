import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Max
import calendar
from decimal import Decimal

from .models import CostProjection
from .serializers import (
    CostProjectionSerializer, 
    CostProjectionBulkSerializer,
    ProjectionRowSerializer,
    ProjectionResponseSerializer
)
from trading.models import Customer, Business, Trade

logger = logging.getLogger(__name__)


class ProjectionMixin:
    """Mixin to provide common helper methods for projection views"""
    
    def _get_business(self, request):
        """Get business for authenticated user."""
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

    def _get_customer(self, request, mprn):
        """Get customer by MPRN scoped to user's business."""
        business, error_response = self._get_business(request)
        if error_response:
            return None, error_response
        
        try:
            customer = Customer.objects.get(mprn=mprn, business=business)
        except Customer.DoesNotExist:
            return None, Response({
                'success': False,
                'message': 'Customer not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        return customer, None

    def _get_prefilled_consumption(self, customer, year, month):
        """Get prefilled consumption from previous year (year - 1) for same month."""
        previous_year = year - 1
        try:
            projection = CostProjection.objects.get(
                customer=customer,
                year=previous_year,
                month=month
            )
            return projection.consumption
        except CostProjection.DoesNotExist:
            return 0


class ProjectionListCreateView(APIView, ProjectionMixin):
    """List and create cost projections."""

    def get(self, request):
        """Get projection data for a specific customer and year.
        
        Query params:
        - mprn: Customer MPRN (10 digits)
        - year: Year
        
        Note: traded_price and cost are calculated dynamically from related Trade model
        """
        mprn = request.query_params.get('mprn')
        year_param = request.query_params.get('year')
        
        if not mprn or not year_param:
            return Response({
                'success': False,
                'message': 'MPRN and year are required.',
                'errors': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year_param)
        except ValueError:
            return Response({
                'success': False,
                'message': 'Year must be a valid integer.',
                'errors': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        customer, error_response = self._get_customer(request, mprn)
        if error_response:
            return error_response
        
        # Get or create projections for all 12 months
        # Note: traded_price and cost are now calculated dynamically via model properties
        rows = []
        for month in range(1, 13):
            no_of_days = calendar.monthrange(year, month)[1]
            
            try:
                projection = CostProjection.objects.get(
                    customer=customer,
                    year=year,
                    month=month
                )
                # Access properties to get dynamically calculated values
                row = {
                    'month': month,
                    'no_of_days': no_of_days,
                    'st_charge': projection.st_charge,
                    'consumption': projection.consumption,
                    'flex_rate': projection.flex_rate,
                    'traded_price': projection.traded_price,  # Calculated dynamically from Trade model
                    'cost': projection.cost  # Calculated dynamically
                }
            except CostProjection.DoesNotExist:
                # Get prefilled consumption from previous year
                consumption = self._get_prefilled_consumption(customer, year, month)
                
                # Create a temporary instance to calculate dynamic values
                temp_projection = CostProjection(
                    customer=customer,
                    year=year,
                    month=month,
                    st_charge=0,
                    consumption=consumption,
                    flex_rate=0
                )
                
                row = {
                    'month': month,
                    'no_of_days': no_of_days,
                    'st_charge': 0,
                    'consumption': consumption,
                    'flex_rate': 0,
                    'traded_price': temp_projection.traded_price,  # Calculated dynamically
                    'cost': temp_projection.cost  # Calculated dynamically
                }
            
            rows.append(row)
        
        response_data = {
            'mprn': mprn,
            'year': year,
            'rows': rows
        }
        
        return Response({
            'success': True,
            'message': 'Projection data retrieved successfully.',
            'data': response_data
        })

    def post(self, request):
        """Save or update projection data for 12 months.
        
        Note: Only st_charge, consumption, and flex_rate are stored.
        traded_price and cost are calculated dynamically from Trade model.
        """
        serializer = CostProjectionBulkSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': 'Please check your input.',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        mprn = serializer.validated_data['mprn']
        year = serializer.validated_data['year']
        projections_data = serializer.validated_data['projections']
        
        customer, error_response = self._get_customer(request, mprn)
        if error_response:
            return error_response
        
        # Process each month's projection
        # Note: traded_price and cost are NOT stored - they're calculated dynamically
        created_count = 0
        updated_count = 0
        
        for proj_data in projections_data:
            month = proj_data.get('month')
            if not month or month < 1 or month > 12:
                continue
            
            st_charge = proj_data.get('st_charge', 0) or 0
            consumption = proj_data.get('consumption', 0) or 0
            flex_rate = proj_data.get('flex_rate', 0) or 0
            
            # Create or update projection (only storing editable fields)
            projection, created = CostProjection.objects.update_or_create(
                customer=customer,
                year=year,
                month=month,
                defaults={
                    'st_charge': st_charge,
                    'consumption': consumption,
                    'flex_rate': flex_rate,
                    # traded_price and cost are calculated dynamically via properties
                }
            )
            
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        logger.info(f"Projection saved for customer {mprn}, year {year}: {created_count} created, {updated_count} updated")
        
        return Response({
            'success': True,
            'message': f'Projection saved successfully. {created_count} created, {updated_count} updated.',
            'data': {
                'mprn': mprn,
                'year': year,
                'created': created_count,
                'updated': updated_count
            }
        })


class ProjectionDetailView(APIView, ProjectionMixin):
    """Retrieve, update, or delete a single projection."""

    def _get_projection(self, request, projection_id):
        """Get projection by ID scoped to user's business."""
        business, error_response = self._get_business(request)
        if error_response:
            return None, error_response
        
        try:
            projection = CostProjection.objects.select_related('customer').get(
                id=projection_id,
                customer__business=business
            )
        except CostProjection.DoesNotExist:
            return None, Response({
                'success': False,
                'message': 'Projection not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        return projection, None

    def get(self, request, projection_id):
        """Get a single projection."""
        projection, error_response = self._get_projection(request, projection_id)
        if error_response:
            return error_response
        
        serializer = CostProjectionSerializer(projection)
        return Response({
            'success': True,
            'message': 'Projection retrieved successfully.',
            'data': serializer.data
        })

    def put(self, request, projection_id):
        """Update a projection."""
        projection, error_response = self._get_projection(request, projection_id)
        if error_response:
            return error_response
        
        serializer = CostProjectionSerializer(projection, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Projection updated: {projection.id}")
            return Response({
                'success': True,
                'message': 'Projection updated successfully.',
                'data': serializer.data
            })
        
        return Response({
            'success': False,
            'message': 'Please check your input.',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, projection_id):
        """Partial update a projection."""
        return self.put(request, projection_id)

    def delete(self, request, projection_id):
        """Delete a projection."""
        projection, error_response = self._get_projection(request, projection_id)
        if error_response:
            return error_response
        
        projection_id = projection.id
        projection.delete()
        logger.info(f"Projection deleted: {projection_id}")
        
        return Response({
            'success': True,
            'message': 'Projection deleted successfully.',
            'data': {}
        })


class CustomerDashboardMixin:
    """Mixin to provide customer-specific dashboard functionality with strict data isolation."""
    
    def _get_customer_for_user(self, request):
        """Get customer profile for authenticated customer user.
        
        Returns:
            tuple: (customer, error_response)
        """
        if not request.user.is_authenticated:
            return None, Response({
                'success': False,
                'message': 'Login required.',
                'errors': {}
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is in Customer group
        is_customer = request.user.groups.filter(name='Customer').exists()
        if not is_customer:
            return None, Response({
                'success': False,
                'message': 'This page is only for customers',
                'errors': {}
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            return None, Response({
                'success': False,
                'message': 'Customer profile not found.',
                'errors': {}
            }, status=status.HTTP_404_NOT_FOUND)
        
        return customer, None
    
    def _get_projection_rows(self, customer, year):
        """Get projection rows for a specific customer and year."""
        rows = []
        for month in range(1, 13):
            no_of_days = calendar.monthrange(year, month)[1]
            
            try:
                projection = CostProjection.objects.get(
                    customer=customer,
                    year=year,
                    month=month
                )
                row = {
                    'month': month,
                    'no_of_days': no_of_days,
                    'st_charge': projection.st_charge,
                    'consumption': projection.consumption,
                    'flex_rate': projection.flex_rate,
                    'traded_price': projection.traded_price,
                    'cost': projection.cost
                }
            except CostProjection.DoesNotExist:
                # Create empty row with defaults
                temp_projection = CostProjection(
                    customer=customer,
                    year=year,
                    month=month,
                    st_charge=0,
                    consumption=0,
                    flex_rate=0
                )
                row = {
                    'month': month,
                    'no_of_days': no_of_days,
                    'st_charge': 0,
                    'consumption': 0,
                    'flex_rate': 0,
                    'traded_price': temp_projection.traded_price,
                    'cost': temp_projection.cost
                }
            
            rows.append(row)
        
        return rows
    
    def _get_trading_pivot_data(self, customer, year):
        """Get trading pivot data for a specific customer and year."""
        from trading.serializers import TradeSerializer
        
        # Get all trades for this customer and year
        trades = Trade.objects.filter(
            customer=customer,
            year=year
        ).order_by('month', 'trade_no')
        
        # Serialize trades
        trade_serializer = TradeSerializer(trades, many=True)
        
        # Build pivot data structure
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        
        # Get all trade numbers for this year
        trade_numbers = sorted(trades.values_list('trade_no', flat=True).distinct())
        
        # Build pivot structure by month
        pivot_data = []
        for month_num in range(1, 13):
            month_trades = trades.filter(month=month_num)
            month_trades_serialized = TradeSerializer(month_trades, many=True).data
            
            # Calculate totals for this month
            total_percent = sum(float(t.get('percent', 0) or 0) for t in month_trades_serialized)
            
            # Calculate weighted average price
            weighted_sum = sum(
                float(t.get('p_therm', 0) or 0) * float(t.get('percent', 0) or 0) 
                for t in month_trades_serialized
            )
            avg_price = weighted_sum / total_percent if total_percent > 0 else 0
            
            pivot_data.append({
                'month': month_num,
                'month_name': months[month_num - 1],
                'trades': month_trades_serialized,
                'total_percent': round(total_percent, 2),
                'avg_price': round(avg_price, 4)
            })
        
        return {
            'trade_numbers': list(trade_numbers),
            'months': pivot_data
        }


class CustomerDashboardDataView(APIView, CustomerDashboardMixin):
    """Get all dashboard data for the logged-in customer."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all dashboard data for logged-in customer.
        
        Returns customer info, trading years, and projection years.
        """
        customer, error_response = self._get_customer_for_user(request)
        if error_response:
            return error_response
        
        # Get available trading years (years with trade data)
        trading_years = Trade.objects.filter(
            customer=customer
        ).values_list('year', flat=True).distinct().order_by('-year')
        
        # Get available projection years
        projection_years = CostProjection.objects.filter(
            customer=customer
        ).values_list('year', flat=True).distinct().order_by('-year')
        
        # Get max year for trading (default)
        max_trading_year = trading_years.first() if trading_years else None
        
        # Get max year for projection (latest available)
        max_projection_year = projection_years.first() if projection_years else None
        
        # Determine default years
        # Trading: max year with trading data
        # Previous Year: last completed year (max trading year - 1 or max projection year - 1)
        # Current Year: latest available projection year
        
        previous_year = None
        if max_trading_year:
            previous_year = max_trading_year
        elif max_projection_year:
            previous_year = max_projection_year - 1
        
        current_year = max_projection_year
        
        return Response({
            'success': True,
            'message': 'Customer dashboard data retrieved successfully.',
            'data': {
                'customer': {
                    'id': customer.id,
                    'mprn': customer.mprn,
                    'name': customer.user.get_full_name() or customer.user.username
                },
                'trading_years': list(trading_years),
                'projection_years': list(projection_years),
                'defaults': {
                    'trading_year': max_trading_year,
                    'previous_year': previous_year,
                    'current_year': current_year
                }
            }
        })


class CustomerTradingDataView(APIView, CustomerDashboardMixin):
    """Get filtered trading data by year for the logged-in customer."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get trading pivot data for logged-in customer for a specific year.
        
        Query params:
        - year: Year (optional, defaults to max available year)
        """
        customer, error_response = self._get_customer_for_user(request)
        if error_response:
            return error_response
        
        year_param = request.query_params.get('year')
        
        # Get available years
        trading_years = Trade.objects.filter(
            customer=customer
        ).values_list('year', flat=True).distinct().order_by('-year')
        
        # Use max year if not specified
        if not year_param:
            year = trading_years.first() if trading_years else None
        else:
            try:
                year = int(year_param)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Year must be a valid integer.',
                    'errors': {}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if not year:
            return Response({
                'success': True,
                'message': 'No trading data available for selected year',
                'data': {
                    'year': None,
                    'pivot_data': None,
                    'available_years': list(trading_years)
                }
            })
        
        # Validate year belongs to this customer
        if year not in trading_years:
            # Check if year exists at all for this customer
            all_customer_years = list(trading_years)
            if all_customer_years:
                return Response({
                    'success': False,
                    'message': 'No trading data available for selected year',
                    'errors': {}
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({
                    'success': False,
                    'message': 'No trading data available for selected year',
                    'errors': {}
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Get trading pivot data
        pivot_data = self._get_trading_pivot_data(customer, year)
        
        return Response({
            'success': True,
            'message': 'Trading data retrieved successfully.',
            'data': {
                'year': year,
                'pivot_data': pivot_data,
                'available_years': list(trading_years)
            }
        })


class CustomerProjectionDataView(APIView, CustomerDashboardMixin):
    """Get projection data by year for the logged-in customer."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get projection data for logged-in customer for a specific year.
        
        Query params:
        - year: Year (optional, defaults to max available year)
        """
        customer, error_response = self._get_customer_for_user(request)
        if error_response:
            return error_response
        
        year_param = request.query_params.get('year')
        
        # Get available years
        projection_years = CostProjection.objects.filter(
            customer=customer
        ).values_list('year', flat=True).distinct().order_by('-year')
        
        # Use max year if not specified
        if not year_param:
            year = projection_years.first() if projection_years else None
        else:
            try:
                year = int(year_param)
            except ValueError:
                return Response({
                    'success': False,
                    'message': 'Year must be a valid integer.',
                    'errors': {}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        if not year:
            return Response({
                'success': True,
                'message': 'Projection data not available',
                'data': {
                    'year': None,
                    'rows': [],
                    'available_years': list(projection_years)
                }
            })
        
        # Get projection rows
        rows = self._get_projection_rows(customer, year)
        
        return Response({
            'success': True,
            'message': 'Projection data retrieved successfully.',
            'data': {
                'year': year,
                'rows': rows,
                'available_years': list(projection_years)
            }
        })


class CalculateCostView(APIView, CustomerDashboardMixin):
    """Calculate cost with custom trade price for the logged-in customer."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Calculate cost with custom trade price values.
        
        Request body:
        {
            "year": 2025,
            "trade_prices": {
                "1": 50.5,  // month: custom trade price
                "2": 51.0,
                ...
            }
        }
        
        Returns calculated costs based on the provided trade prices.
        """
        customer, error_response = self._get_customer_for_user(request)
        if error_response:
            return error_response
        
        year = request.data.get('year')
        trade_prices = request.data.get('trade_prices', {})
        
        if not year:
            return Response({
                'success': False,
                'message': 'Year is required.',
                'errors': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            year = int(year)
        except ValueError:
            return Response({
                'success': False,
                'message': 'Year must be a valid integer.',
                'errors': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate year belongs to this customer (has projection data)
        projection_years = CostProjection.objects.filter(
            customer=customer
        ).values_list('year', flat=True).distinct()
        
        if year not in projection_years:
            return Response({
                'success': False,
                'message': 'No projection data available for the specified year.',
                'errors': {}
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate costs for each month
        results = []
        for month in range(1, 13):
            no_of_days = calendar.monthrange(year, month)[1]
            
            try:
                projection = CostProjection.objects.get(
                    customer=customer,
                    year=year,
                    month=month
                )
                
                st_charge = Decimal(str(projection.st_charge))
                consumption = Decimal(str(projection.consumption))
                flex_rate = Decimal(str(projection.flex_rate))
                
            except CostProjection.DoesNotExist:
                st_charge = Decimal('0')
                consumption = Decimal('0')
                flex_rate = Decimal('0')
            
            # Get custom trade price or use default
            custom_price = trade_prices.get(str(month)) or trade_prices.get(month)
            if custom_price is not None:
                tp = Decimal(str(custom_price))
            else:
                # Get default traded price from Trade model
                temp_projection = CostProjection(
                    customer=customer,
                    year=year,
                    month=month,
                    st_charge=0,
                    consumption=0,
                    flex_rate=0
                )
                tp = temp_projection.traded_price
            
            # Calculate cost using the formula:
            # Cost = (st_charge * days_in_month / 100) + (consumption * (flex_rate + tp/29.3071) / 100)
            st_charge_component = st_charge * Decimal(no_of_days) / Decimal('100')
            traded_price_per_kwh = tp / Decimal('29.3071')
            unit_component = (consumption * (flex_rate + traded_price_per_kwh)) / Decimal('100')
            total_cost = st_charge_component + unit_component
            
            results.append({
                'month': month,
                'no_of_days': no_of_days,
                'st_charge': float(st_charge),
                'consumption': float(consumption),
                'flex_rate': float(flex_rate),
                'trade_price': float(tp),
                'cost': float(round(total_cost, 2))
            })
        
        return Response({
            'success': True,
            'message': 'Cost calculated successfully.',
            'data': {
                'year': year,
                'rows': results
            }
        })
