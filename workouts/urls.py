from django.urls import path
from .views import (
    WorkoutPlanListCreateView,
    WorkoutTaskListCreateView,
    WorkoutTaskDetailView
)

urlpatterns = [
    path('plans/', WorkoutPlanListCreateView.as_view(), name='plan_list_create'),
    path('tasks/', WorkoutTaskListCreateView.as_view(), name='task_list_create'),
    path('tasks/<int:pk>/', WorkoutTaskDetailView.as_view(), name='task_detail'),
]