from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from gyms.models import GymBranch
from workouts.models import WorkoutPlan, WorkoutTask


class Command(BaseCommand):
    help = 'Create test data for the gym management system'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating test data...')

        # Create Super Admin
        super_admin, created = User.objects.get_or_create(
            email='admin@gmail.com',
            defaults={
                'role': 'SUPER_ADMIN',
            }
        )
        if created:
            super_admin.set_password('Admin@123')
            super_admin.save()
            self.stdout.write(self.style.SUCCESS(
                f'✓ Created Super Admin: {super_admin.email}'
            ))

        # Create Gym Branches
        branch1, _ = GymBranch.objects.get_or_create(
            name='Downtown Fitness',
            defaults={'location': '123 Main Street, Downtown'}
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Created Branch: {branch1.name}'))

        branch2, _ = GymBranch.objects.get_or_create(
            name='Uptown Gym',
            defaults={'location': '456 North Avenue, Uptown'}
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Created Branch: {branch2.name}'))

        # Create Managers
        manager1, created = User.objects.get_or_create(
            email='manager@gmail.com',
            defaults={
                'role': 'MANAGER',
                'gym_branch': branch1,
            }
        )
        if created:
            manager1.set_password('Manager@123')
            manager1.save()

        manager2, created = User.objects.get_or_create(
            email='manager2@gmail.com',
            defaults={
                'role': 'MANAGER',
                'gym_branch': branch2,
            }
        )
        if created:
            manager2.set_password('Manager@123')
            manager2.save()

        # Create Trainers
        trainer1, created = User.objects.get_or_create(
            email='trainer@gmail.com',
            defaults={
                'role': 'TRAINER',
                'gym_branch': branch1,
            }
        )
        if created:
            trainer1.set_password('Trainer@123')
            trainer1.save()

        trainer2, created = User.objects.get_or_create(
            email='trainer2@gmail.com',
            defaults={
                'role': 'TRAINER',
                'gym_branch': branch1,
            }
        )
        if created:
            trainer2.set_password('Trainer@123')
            trainer2.save()

        trainer3, created = User.objects.get_or_create(
            email='trainer3@gmail.com',
            defaults={
                'role': 'TRAINER',
                'gym_branch': branch2,
            }
        )
        if created:
            trainer3.set_password('Trainer@123')
            trainer3.save()

        # Create Members
        member1, created = User.objects.get_or_create(
            email='member@gmail.com',
            defaults={
                'role': 'MEMBER',
                'gym_branch': branch1,
            }
        )
        if created:
            member1.set_password('Member@123')
            member1.save()

        member2, created = User.objects.get_or_create(
            email='member2@gmail.com',
            defaults={
                'role': 'MEMBER',
                'gym_branch': branch1,
            }
        )
        if created:
            member2.set_password('Member@123')
            member2.save()

        member3, created = User.objects.get_or_create(
            email='member3@gmail.com',
            defaults={
                'role': 'MEMBER',
                'gym_branch': branch2,
            }
        )
        if created:
            member3.set_password('Member@123')
            member3.save()

        # Create Workout Plans
        plan1, _ = WorkoutPlan.objects.get_or_create(
            title='Beginner Strength Training',
            defaults={
                'description': 'A comprehensive strength training program for beginners',
                'created_by': trainer1,
                'gym_branch': branch1,
            }
        )

        plan2, _ = WorkoutPlan.objects.get_or_create(
            title='Advanced Cardio',
            defaults={
                'description': 'High-intensity cardio workout for advanced members',
                'created_by': trainer1,
                'gym_branch': branch1,
            }
        )

        plan3, _ = WorkoutPlan.objects.get_or_create(
            title='Yoga & Flexibility',
            defaults={
                'description': 'Improve flexibility and balance through yoga',
                'created_by': trainer3,
                'gym_branch': branch2,
            }
        )

        # Create Workout Tasks
        WorkoutTask.objects.get_or_create(
            workout_plan=plan1,
            member=member1,
            defaults={
                'status': 'PENDING',
                'due_date': timezone.now().date() + timedelta(days=7),
            }
        )

        WorkoutTask.objects.get_or_create(
            workout_plan=plan2,
            member=member1,
            defaults={
                'status': 'IN_PROGRESS',
                'due_date': timezone.now().date() + timedelta(days=14),
            }
        )

        WorkoutTask.objects.get_or_create(
            workout_plan=plan1,
            member=member2,
            defaults={
                'status': 'COMPLETED',
                'due_date': timezone.now().date() + timedelta(days=5),
            }
        )

        WorkoutTask.objects.get_or_create(
            workout_plan=plan3,
            member=member3,
            defaults={
                'status': 'PENDING',
                'due_date': timezone.now().date() + timedelta(days=10),
            }
        )

        self.stdout.write(self.style.SUCCESS('\n✅ Test data created successfully!'))
        self.stdout.write('\n📋 Test User Credentials:')
        self.stdout.write('---------------------------')
        self.stdout.write('Super Admin: admin@gmail.com / Admin@123')
        self.stdout.write('Manager: manager@gmail.com / Manager@123')
        self.stdout.write('Manager: manager2@gmail.com / Manager@123')
        self.stdout.write('Trainer: trainer@gmail.com / Trainer@123')
        self.stdout.write('Trainer: trainer2@gmail.com / Trainer@123')
        self.stdout.write('Trainer: trainer3@gmail.com / Trainer@123')
        self.stdout.write('Member: member@gmail.com / Member@123')
        self.stdout.write('Member: member2@gmail.com / Member@123')
        self.stdout.write('Member: member3@gmail.com / Member@123')
