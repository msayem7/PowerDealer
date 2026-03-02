import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import calendar

from .models import CostProjection
from .serializers import (
    CostProjectionSerializer, 
    CostProjectionBulkSerializer,
    ProjectionRowSerializer,
    ProjectionResponseSerializer
)
from trading.models import Customer, Business

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
