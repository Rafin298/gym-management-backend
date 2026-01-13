from rest_framework import permissions


class IsSuperAdmin(permissions.BasePermission):
    """Only Super Admin can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'SUPER_ADMIN'
        )


class IsManager(permissions.BasePermission):
    """Only Manager can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'MANAGER'
        )


class IsTrainer(permissions.BasePermission):
    """Only Trainer can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'TRAINER'
        )


class IsMember(permissions.BasePermission):
    """Only Member can access"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'MEMBER'
        )


class IsSameBranch(permissions.BasePermission):
    """
    Ensure users can only access data from their own branch
    Super Admin can access all branches
    """
    
    def has_object_permission(self, request, view, obj):
        # Super Admin can access everything
        if request.user.role == 'SUPER_ADMIN':
            return True
        
        # Check if object has gym_branch attribute
        if hasattr(obj, 'gym_branch'):
            return obj.gym_branch == request.user.gym_branch
        
        # For User objects, check their gym_branch
        if hasattr(obj, 'role'):
            return obj.gym_branch == request.user.gym_branch
        
        return False