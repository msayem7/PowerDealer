"""
Custom exception handler for consistent API error responses.

Response format:
{
    "success": false,
    "message": "User-friendly message",
    "errors": {}  # Field-specific errors if validation fails
}
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent error format.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Get view and request info for logging
    view = context.get('view', None)
    request = context.get('request', None)
    view_name = view.__class__.__name__ if view else 'Unknown'
    
    if response is not None:
        # Map status codes to friendly messages
        status_messages = {
            400: "Please check your input.",
            401: "Login required.",
            403: "You don't have permission to perform this action.",
            404: "The requested resource was not found.",
            405: "This action is not allowed.",
            500: "Something went wrong. Please try again later.",
        }
        
        # Get friendly message based on status code
        friendly_message = status_messages.get(
            response.status_code, 
            "We couldn't process your request right now."
        )
        
        # Handle validation errors (field-specific)
        errors = {}
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if key in ['detail', 'error', 'message']:
                    # Use the backend message if it's user-friendly
                    if isinstance(value, str):
                        friendly_message = value
                else:
                    # Field-specific errors
                    if isinstance(value, list):
                        errors[key] = value[0] if len(value) == 1 else value
                    else:
                        errors[key] = value
        elif isinstance(response.data, list):
            errors['non_field_errors'] = response.data
        
        # Log the error (with technical details for developers)
        logger.warning(
            f"API Error in {view_name}: status={response.status_code}, "
            f"errors={errors}, user={getattr(request, 'user', 'anonymous')}"
        )
        
        # Return consistent format
        response.data = {
            'success': False,
            'message': friendly_message,
            'errors': errors
        }
    else:
        # Unhandled exception - log as error
        logger.error(
            f"Unhandled exception in {view_name}: {str(exc)}",
            exc_info=True
        )
        
        # Return generic error response
        return Response({
            'success': False,
            'message': "Something went wrong. Please try again later.",
            'errors': {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response
