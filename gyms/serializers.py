from rest_framework import serializers
from .models import GymBranch


class GymBranchSerializer(serializers.ModelSerializer):
    trainer_count = serializers.IntegerField(read_only=True)
    member_count = serializers.SerializerMethodField()
    manager_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GymBranch
        fields = [
            'id', 'name', 'location', 'created_at',
            'trainer_count', 'member_count', 'manager_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_member_count(self, obj):
        """Get count of members in this branch"""
        return obj.users.filter(role='MEMBER').count()
    
    def get_manager_count(self, obj):
        """Get count of managers in this branch"""
        return obj.users.filter(role='MANAGER').count()
    
    def validate_name(self, value):
        """Ensure branch name is unique"""
        if not value or not value.strip():
            raise serializers.ValidationError('Branch name cannot be empty')
        return value.strip()
    
    def validate_location(self, value):
        """Ensure location is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError('Location cannot be empty')
        return value.strip()