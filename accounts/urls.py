from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView, CurrentUserView, UserListCreateView, SuperAdminUserView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('users/', UserListCreateView.as_view(), name='user_list_create'),
    path('admin/users/', SuperAdminUserView.as_view(), name='admin_user_management'),
]