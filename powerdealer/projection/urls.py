from django.urls import path
from .views import ProjectionListCreateView, ProjectionDetailView

urlpatterns = [
    path('projection/', ProjectionListCreateView.as_view(), name='projection-list-create'),
    path('projection/<int:projection_id>/', ProjectionDetailView.as_view(), name='projection-detail'),
]
