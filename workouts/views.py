from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import WorkoutPlan, WorkoutTask
from .serializers import (
    WorkoutPlanSerializer, 
    WorkoutTaskSerializer, 
    WorkoutTaskUpdateSerializer
)


class WorkoutPlanListCreateView(APIView):
    """
    Trainer can create workout plans
    Trainer and Manager can list plans from their branch
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List workout plans based on user role"""
        user = request.user
        
        if user.role == 'SUPER_ADMIN':
            plans = WorkoutPlan.objects.all()
        elif user.role in ['MANAGER', 'TRAINER']:
            plans = WorkoutPlan.objects.filter(gym_branch=user.gym_branch)
        else:
            # Members cannot view workout plans directly
            return Response(
                {'detail': 'Members cannot view workout plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        plans = plans.select_related('created_by', 'gym_branch')
        serializer = WorkoutPlanSerializer(plans, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create workout plan (Trainer only)"""
        if request.user.role != 'TRAINER':
            return Response(
                {'detail': 'Only trainers can create workout plans'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = WorkoutPlanSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            plan = serializer.save()
            return Response(
                WorkoutPlanSerializer(plan).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class WorkoutTaskListCreateView(APIView):
    """
    Trainer can create and assign tasks
    Members can view their own tasks
    Manager and Trainer can view all tasks in their branch
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List workout tasks based on user role"""
        user = request.user
        
        if user.role == 'SUPER_ADMIN':
            tasks = WorkoutTask.objects.all()
        elif user.role == 'MEMBER':
            # Members can only see their own tasks
            tasks = WorkoutTask.objects.filter(member=user)
        elif user.role in ['MANAGER', 'TRAINER']:
            # Manager and Trainer can see all tasks in their branch
            tasks = WorkoutTask.objects.filter(
                workout_plan__gym_branch=user.gym_branch
            )
        else:
            return Response(
                {'detail': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Optional status filter
        task_status = request.query_params.get('status')
        if task_status:
            tasks = tasks.filter(status=task_status.upper())
        
        tasks = tasks.select_related(
            'workout_plan', 
            'member', 
            'workout_plan__gym_branch'
        )
        
        serializer = WorkoutTaskSerializer(tasks, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        """Create and assign workout task (Trainer only)"""
        if request.user.role != 'TRAINER':
            return Response(
                {'detail': 'Only trainers can assign workout tasks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = WorkoutTaskSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verify trainer can only assign tasks within their branch
            workout_plan = serializer.validated_data['workout_plan']
            if workout_plan.gym_branch != request.user.gym_branch:
                return Response(
                    {'detail': 'You can only assign tasks for workout plans in your branch'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            task = serializer.save()
            return Response(
                WorkoutTaskSerializer(task).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class WorkoutTaskDetailView(APIView):
    """
    Update task status
    Trainer can update any task in their branch
    Member can only update their own tasks
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return WorkoutTask.objects.select_related(
                'workout_plan',
                'member',
                'workout_plan__gym_branch'
            ).get(pk=pk)
        except WorkoutTask.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """Get task details"""
        task = self.get_object(pk)
        if not task:
            return Response(
                {'detail': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions
        user = request.user
        if user.role == 'MEMBER' and task.member != user:
            return Response(
                {'detail': 'You can only view your own tasks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if user.role in ['TRAINER', 'MANAGER']:
            if task.workout_plan.gym_branch != user.gym_branch:
                return Response(
                    {'detail': 'Task not found in your branch'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = WorkoutTaskSerializer(task)
        return Response(serializer.data)
    
    def patch(self, request, pk):
        """Update task status"""
        task = self.get_object(pk)
        if not task:
            return Response(
                {'detail': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user = request.user
        
        # Members can only update their own tasks
        if user.role == 'MEMBER' and task.member != user:
            return Response(
                {'detail': 'You can only update your own tasks'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Trainers can only update tasks in their branch
        if user.role == 'TRAINER':
            if task.workout_plan.gym_branch != user.gym_branch:
                return Response(
                    {'detail': 'You can only update tasks in your branch'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = WorkoutTaskUpdateSerializer(
            task, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(WorkoutTaskSerializer(task).data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )