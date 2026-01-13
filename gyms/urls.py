from django.urls import path
from .views import GymBranchListCreateView, GymBranchDetailView

urlpatterns = [
    path('branches/', GymBranchListCreateView.as_view(), name='branch_list_create'),
    path('branches/<int:pk>/', GymBranchDetailView.as_view(), name='branch_detail'),
]