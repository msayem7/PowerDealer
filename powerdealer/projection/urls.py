from django.urls import path
from .views import (
    ProjectionListCreateView, 
    ProjectionDetailView,
    CustomerDashboardDataView,
    CustomerTradingDataView,
    CustomerProjectionDataView,
    CalculateCostView
)

urlpatterns = [
    path('projection/', ProjectionListCreateView.as_view(), name='projection-list-create'),
    path('projection/<int:projection_id>/', ProjectionDetailView.as_view(), name='projection-detail'),
    
    # Customer Dashboard endpoints
    path('customer-dashboard-data/', CustomerDashboardDataView.as_view(), name='customer-dashboard-data'),
    path('customer-trading-data/', CustomerTradingDataView.as_view(), name='customer-trading-data'),
    path('customer-projection-data/', CustomerProjectionDataView.as_view(), name='customer-projection-data'),
    path('calculate-cost/', CalculateCostView.as_view(), name='calculate-cost'),
]
