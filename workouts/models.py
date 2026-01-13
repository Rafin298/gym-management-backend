from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User
from gyms.models import GymBranch


class WorkoutPlan(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_plans',
        limit_choices_to={'role': 'TRAINER'}
    )
    gym_branch = models.ForeignKey(
        GymBranch,
        on_delete=models.CASCADE,
        related_name='workout_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_plans'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.gym_branch.name}"
    
    def clean(self):
        # Ensure trainer belongs to the same branch
        if self.created_by and self.gym_branch:
            if self.created_by.gym_branch != self.gym_branch:
                raise ValidationError(
                    'Trainer must belong to the same gym branch as the workout plan'
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class WorkoutTask(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    
    workout_plan = models.ForeignKey(
        WorkoutPlan,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='workout_tasks',
        limit_choices_to={'role': 'MEMBER'}
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'workout_tasks'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.workout_plan.title} - {self.member.email}"
    
    def clean(self):
        # Ensure member belongs to the same branch as the workout plan
        if self.member and self.workout_plan:
            if self.member.gym_branch != self.workout_plan.gym_branch:
                raise ValidationError(
                    'Cannot assign task to member from a different gym branch'
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)