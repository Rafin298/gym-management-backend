from rest_framework import serializers
from .models import WorkoutPlan, WorkoutTask
from django.utils import timezone


class WorkoutPlanSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(
        source='created_by.email', read_only=True
    )
    gym_branch_name = serializers.CharField(
        source='gym_branch.name', read_only=True
    )
    task_count = serializers.SerializerMethodField()

    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    gym_branch = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = WorkoutPlan
        fields = [
            'id', 'title', 'description', 'created_by', 'created_by_email',
            'gym_branch', 'gym_branch_name', 'task_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'gym_branch', 'created_at']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty')
        return value.strip()

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user:
            raise serializers.ValidationError("User not found in request.")

        if not user.gym_branch:
            raise serializers.ValidationError({
                'gym_branch': 'You must be assigned to a gym branch to create workout plans'
            })

        validated_data['created_by'] = user
        validated_data['gym_branch'] = user.gym_branch
        return super().create(validated_data)


class WorkoutTaskSerializer(serializers.ModelSerializer):
    workout_plan_title = serializers.CharField(source='workout_plan.title', read_only=True)
    member_email = serializers.EmailField(source='member.email', read_only=True)
    gym_branch = serializers.CharField(source='workout_plan.gym_branch.name', read_only=True)
    
    class Meta:
        model = WorkoutTask
        fields = [
            'id', 'workout_plan', 'workout_plan_title',
            'member', 'member_email', 'status', 'due_date',
            'gym_branch', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_due_date(self, value):
        """Ensure due date is not in the past"""
        if value < timezone.now().date():
            raise serializers.ValidationError('Due date cannot be in the past')
        return value
    
    def validate(self, attrs):
        """Validate task assignment"""
        workout_plan = attrs.get('workout_plan')
        member = attrs.get('member')
        
        # Ensure member and workout plan are from the same branch
        if workout_plan and member:
            if workout_plan.gym_branch != member.gym_branch:
                raise serializers.ValidationError({
                    'member': 'Cannot assign task to member from a different gym branch'
                })
        
        return attrs


class WorkoutTaskUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating task status only"""
    
    class Meta:
        model = WorkoutTask
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status transition"""
        valid_statuses = ['PENDING', 'IN_PROGRESS', 'COMPLETED']
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            )
        return value