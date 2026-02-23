from django.urls import path
from .views import (
    SignupView, LoginView, BusinessDetailView, MeView, HealthCheckView,
    CustomerListCreateView, CustomerDetailView,
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health'),
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('business/', BusinessDetailView.as_view(), name='business'),
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('customers/<str:mprn>/', CustomerDetailView.as_view(), name='customer-detail'),
]
