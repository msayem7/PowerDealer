from django.urls import path
from .views import SignupView, LoginView, BusinessDetailView, MeView

urlpatterns = [
    path('auth/signup/', SignupView.as_view(), name='signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/me/', MeView.as_view(), name='me'),
    path('business/', BusinessDetailView.as_view(), name='business'),
]
