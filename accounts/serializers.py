from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    gym_branch_name = serializers.CharField(source='gym_branch.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'role', 
            'gym_branch', 'gym_branch_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, attrs):
        """Validate user creation based on role and branch"""
        role = attrs.get('role')
        gym_branch = attrs.get('gym_branch')
        
        # Super Admin should not have a branch
        if role == 'SUPER_ADMIN' and gym_branch:
            raise serializers.ValidationError({
                'gym_branch': 'Super Admin cannot be assigned to a gym branch'
            })
        
        # Other roles must have a branch
        if role != 'SUPER_ADMIN' and not gym_branch:
            raise serializers.ValidationError({
                'gym_branch': f'{role} must be assigned to a gym branch'
            })
        
        # Check manager limit (max 1 per branch)
        if role == 'MANAGER' and gym_branch:
            if not gym_branch.can_add_manager():
                raise serializers.ValidationError({
                    'gym_branch': f'This gym branch already has a manager. Maximum allowed is 1.'
                })
        
        # Check trainer limit (max 3 per branch)
        if role == 'TRAINER' and gym_branch:
            if not gym_branch.can_add_trainer():
                raise serializers.ValidationError({
                    'gym_branch': f'This gym branch already has 3 trainers. Cannot add more.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create user with hashed password"""
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile (current user)"""
    gym_branch_name = serializers.CharField(source='gym_branch.name', read_only=True)
    gym_branch_location = serializers.CharField(source='gym_branch.location', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'role', 
            'gym_branch', 'gym_branch_name', 'gym_branch_location',
            'created_at'
        ]
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    """Serializer for login request"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)