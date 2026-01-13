from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import GymBranch
from .serializers import GymBranchSerializer
from accounts.permissions import IsSuperAdmin


class GymBranchListCreateView(APIView):
    """
    Super Admin can create and list gym branches
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get(self, request):
        """List all gym branches"""
        branches = GymBranch.objects.all()
        serializer = GymBranchSerializer(branches, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create a new gym branch"""
        serializer = GymBranchSerializer(data=request.data)
        if serializer.is_valid():
            branch = serializer.save()
            return Response(
                GymBranchSerializer(branch).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class GymBranchDetailView(APIView):
    """
    Get, update or delete a gym branch (Super Admin only)
    """
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    def get_object(self, pk):
        try:
            return GymBranch.objects.get(pk=pk)
        except GymBranch.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Get gym branch details"""
        branch = self.get_object(pk)
        if not branch:
            return Response(
                {'detail': 'Gym branch not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = GymBranchSerializer(branch)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """Update gym branch"""
        branch = self.get_object(pk)
        if not branch:
            return Response(
                {'detail': 'Gym branch not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = GymBranchSerializer(branch, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        """Delete gym branch"""
        branch = self.get_object(pk)
        if not branch:
            return Response(
                {'detail': 'Gym branch not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        branch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)