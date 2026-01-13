from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'SUPER_ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('SUPER_ADMIN', 'Super Admin'),
        ('MANAGER', 'Gym Manager'),
        ('TRAINER', 'Trainer'),
        ('MEMBER', 'Member'),
    ]
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    gym_branch = models.ForeignKey(
        'gyms.GymBranch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users'
    )
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.email} ({self.role})"
    
    def clean(self):
        # Super Admin should not have a gym branch
        if self.role == 'SUPER_ADMIN' and self.gym_branch:
            raise ValidationError('Super Admin cannot be assigned to a gym branch')
        
        # Other roles must have a gym branch
        if self.role != 'SUPER_ADMIN' and not self.gym_branch:
            raise ValidationError(f'{self.get_role_display()} must be assigned to a gym branch')
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)