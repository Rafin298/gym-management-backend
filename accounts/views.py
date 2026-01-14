from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, UserProfileSerializer, LoginSerializer
from .permissions import IsManager, IsSuperAdmin
from rest_framework.pagination import PageNumberPagination

class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(email=email, password=password)
        
        if user is None:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not user.is_active:
            return Response(
                {'detail': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserProfileSerializer(user).data
        })


class CurrentUserView(APIView):
    """Get current user profile"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class UserListCreateView(APIView):
    """
    Manager can create trainers and members for their branch
    Manager can list all users in their branch
    """
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request):
        """List all users in manager's branch"""
        users = User.objects.filter(
            gym_branch=request.user.gym_branch
        ).select_related('gym_branch')
        
        # Optional role filter
        role = request.query_params.get('role')
        if role:
            users = users.filter(role=role.upper())
    
        paginator = PageNumberPagination()

        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """Create trainer or member for manager's branch"""
        data = request.data.copy()
        
        # Get the role from request
        role = data.get('role', '').upper()
        
        # Manager can only create TRAINER or MEMBER
        if role not in ['TRAINER', 'MEMBER']:
            return Response(
                {'detail': 'Manager can only create Trainer or Member roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Auto-assign manager's branch
        data['gym_branch'] = request.user.gym_branch.id
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class SuperAdminUserView(APIView):
    """
    Super Admin can create managers and view all users
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get(self, request):
        """List all users (Super Admin can see all)"""
        users = User.objects.all().select_related('gym_branch')
        
        # Optional filters
        role = request.query_params.get('role')
        branch_id = request.query_params.get('branch')
        
        if role:
            users = users.filter(role=role.upper())
        if branch_id:
            users = users.filter(gym_branch_id=branch_id)
        
        paginator = PageNumberPagination()

        page = paginator.paginate_queryset(users, request)
        serializer = UserSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        """Create manager or any other user"""
        data = request.data.copy()
        role = data.get('role', '').upper()
        
        # Super Admin can create any role except another Super Admin
        if role == 'SUPER_ADMIN':
            return Response(
                {'detail': 'Cannot create another Super Admin via API'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate that branch is provided for non-super-admin roles
        if role != 'SUPER_ADMIN' and not data.get('gym_branch'):
            return Response(
                {'detail': f'{role} must be assigned to a gym branch'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )