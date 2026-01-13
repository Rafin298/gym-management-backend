from django.db import models
from django.core.exceptions import ValidationError


class GymBranch(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'gym_branches'
        ordering = ['-created_at']
        verbose_name_plural = 'Gym Branches'
    
    def __str__(self):
        return f"{self.name} - {self.location}"
    
    def trainer_count(self):
        """Get count of trainers in this branch"""
        return self.users.filter(role='TRAINER').count()
    
    def can_add_trainer(self):
        """Check if branch can have more trainers (max 3)"""
        return self.trainer_count() < 3
    
    def validate_trainer_limit(self):
        """Validate trainer limit before adding"""
        if not self.can_add_trainer():
            raise ValidationError(
                f'This gym branch already has {self.trainer_count()} trainers. Maximum allowed is 3.'
            )