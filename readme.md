# Gym Management & Member Workout System API

A comprehensive REST API backend for managing gym branches, trainers, members, and workout assignments using Django REST Framework and PostgreSQL.

## 🌟 Features

- **Multi-branch Management**: Support for multiple gym locations
- **Role-based Access Control**: Super Admin, Manager, Trainer, and Member roles
- **JWT Authentication**: Secure token-based authentication
- **Workout Management**: Create plans and assign tasks to members
- **Branch Isolation**: Users can only access data from their assigned branch
- **Trainer Limits**: Maximum 3 trainers per branch (enforced)
- **Pagination**: All list endpoints support pagination
- **Rate Limit**: Rate Limit is Applied

## 🚀 Live API

**Base URL**: `https://rafins-gym-management-backend.vercel.app/api/`

## 📋 Test User Credentials

| Role | Email | Password | Branch |
|------|-------|----------|--------|
| Super Admin | admin@gmail.com | Admin@123 | N/A |
| Manager | manager@gmail.com | Manager@123 | Downtown Fitness |
| Manager | manager2@gmail.com | Manager@123 | Uptown Gym |
| Trainer | trainer@gmail.com | Trainer@123 | Downtown Fitness |
| Trainer | trainer2@gmail.com | Trainer@123 | Downtown Fitness |
| Trainer | trainer3@gmail.com | Trainer@123 | Uptown Gym |
| Member | member@gmail.com | Member@123 | Downtown Fitness |
| Member | member2@gmail.com | Member@123 | Downtown Fitness |
| Member | member3@gmail.com | Member@123 | Uptown Gym |

## 🏗️ Project Setup

### Prerequisites

- Python 3.14
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Rafin298/gym-management-backend.git
cd gym-management-backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup PostgreSQL Database**
- Create using pgadmin
- Or use online hosted postgres database

5. **Configure Environment Variables**

Create a `.env` file in the project root and add database configs and other configs:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=gym_management_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
```

6. **Run Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create Test Data**
```bash
python manage.py create_test_data
```

8. **Run Development Server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| POST | `/api/auth/login/` | User login | Public |
| POST | `/api/auth/refresh/` | Refresh access token | Public |
| GET | `/api/auth/me/` | Get current user profile | Authenticated |

### Gym Branches

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/gyms/branches/` | List all branches | Super Admin |
| POST | `/api/gyms/branches/` | Create new branch | Super Admin |
| GET | `/api/gyms/branches/{id}/` | Get branch details | Super Admin |
| PUT | `/api/gyms/branches/{id}/` | Update branch | Super Admin |
| DELETE | `/api/gyms/branches/{id}/` | Delete branch | Super Admin |

### Users

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/auth/users/` | List users in branch | Manager |
| POST | `/api/auth/users/` | Create trainer/member | Manager |
| GET | `/api/auth/admin/users/` | List all users | Super Admin |
| POST | `/api/auth/admin/users/` | Create manager/trainer/member | Super Admin |

### Workout Plans

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/workouts/plans/` | List workout plans | Manager, Trainer |
| POST | `/api/workouts/plans/` | Create workout plan | Trainer |

### Workout Tasks

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| GET | `/api/workouts/tasks/` | List tasks | All roles (filtered) |
| POST | `/api/workouts/tasks/` | Assign task to member | Trainer |
| GET | `/api/workouts/tasks/{id}/` | Get task details | Owner/Trainer/Manager |
| PATCH | `/api/workouts/tasks/{id}/` | Update task status | Owner/Trainer |

## 🔐 Authentication

All endpoints (except login and refresh) require authentication using JWT tokens.

### Login Flow

1. **Login** to get tokens:
```bash
POST /api/auth/login/
{
  "email": "trainer@gmail.com",
  "password": "Trainer@123"
}
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 5,
    "email": "trainer@gmail.com",
    "role": "TRAINER",
    "gym_branch": 1,
    "gym_branch_name": "Downtown Fitness"
  }
}
```

2. **Use access token** in subsequent requests:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

3. **Refresh token** when access token expires:
```bash
POST /api/auth/refresh/
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## 👥 User Roles & Permissions

### Super Admin
- Create and manage gym branches
- Create managers for any branch
- View all data across all branches
- Cannot be assigned to a specific branch
- Can create any user role except other Super Admins

### Gym Manager
- Manage one gym branch
- Create trainers and members for their branch only
- View all workout plans and tasks in their branch
- Cannot create other managers or super admins
- Maximum 1 manager per branch

### Trainer
- Belongs to one gym branch
- Create workout plans for their branch
- Assign workout tasks to members in their branch
- Update task statuses
- Maximum 3 trainers per branch

### Member
- Belongs to one gym branch
- View only their assigned workout tasks
- Update status of their own tasks (PENDING → IN_PROGRESS → COMPLETED)
- Cannot view workout plans directly

## 🛡️ Business Rules Enforcement

1. **Branch Isolation**: Users can only access data from their assigned branch (except Super Admin)
2. **Trainer Limit**: Maximum 3 trainers per gym branch (enforced at creation)
3. **Manager Limit**: Maximum 1 manager per gym branch (enforced at creation)
4. **Cross-branch Prevention**: Trainers cannot assign tasks to members from other branches
5. **Task Ownership**: Members can only view and update their own tasks
6. **Role Restrictions**: 
   - Managers can only create trainers and members, not other managers
   - Super Admin can create managers, trainers, and members (but not other Super Admins)
7. **Branch Assignment**: 
   - Super Admin: No branch assignment allowed
   - All other roles: Branch assignment required

## 📦 Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│   User          │
├─────────────────┤
│ id (PK)         │
│ email           │
│ password        │
│ role            │
│ gym_branch (FK) │◄────┐
│ created_at      │     │
└─────────────────┘     │
                        │
┌─────────────────┐     │
│   GymBranch     │     │
├─────────────────┤     │
│ id (PK)         │─────┘
│ name            │
│ location        │
│ created_at      │
└────┬────────────┘
     │
     │
     │    ┌─────────────────┐
     └────►  WorkoutPlan    │
          ├─────────────────┤
          │ id (PK)         │
          │ title           │
          │ description     │
          │ created_by (FK) │
          │ gym_branch (FK) │
          │ created_at      │
          └────┬────────────┘
               │
               │
          ┌────▼────────────┐
          │  WorkoutTask    │
          ├─────────────────┤
          │ id (PK)         │
          │ workout_plan(FK)│
          │ member (FK)     │
          │ status          │
          │ due_date        │
          │ created_at      |
          └─────────────────┘
```

## 🧪 Testing with Postman

### Import Postman Collection

1. Open Postman
2. Click **Import**
3. Select the file: `postman/Gym Management System API.postman_collection.json`
4. The collection will include pre-configured requests for all endpoints

### Environment Variables

Set these variables in Postman:

- `base_url`: Your API base URL (e.g., `http://localhost:8000/api`)
- `access_token`: Will be auto-set after login
- `refresh_token`: Will be auto-set after login

### Testing Flow

1. **Login as Super Admin** → Create gym branches, create managers
2. **Login as Manager** → Create trainers and members
3. **Login as Trainer** → Create workout plans and assign tasks
4. **Login as Member** → View and update own tasks

## 🔍 Example API Usage

### Create Manager (as Super Admin)

```bash
POST /api/auth/admin/users/
Authorization: Bearer {super_admin_access_token}

{
  "email": "newmanager@gym.com",
  "password": "Manager@123",
  "role": "MANAGER",
  "gym_branch": 1
}
```

### Create Workout Plan (as Trainer)

```bash
POST /api/workouts/plans/
Authorization: Bearer {trainer_access_token}

{
  "title": "Weight Loss Program",
  "description": "8-week intensive weight loss workout plan"
}
```

### Assign Task to Member (as Trainer)

```bash
POST /api/workouts/tasks/
Authorization: Bearer {trainer_access_token}

{
  "workout_plan": 1,
  "member": 7,
  "due_date": "2026-02-01"
}
```

### Update Task Status (as Member)

```bash
PATCH /api/workouts/tasks/1/
Authorization: Bearer {member_access_token}

{
  "status": "COMPLETED"
}
```

## 🛠️ Project Structure

```
gym-management-backend/
├── config/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/             # User authentication & management
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── permissions.py
│   └── urls.py
├── gyms/                 # Gym branch management
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── workouts/             # Workout plans & tasks
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── postman/              # API collection
│   └── Gym Management System API.postman_collection.json
├── postgres_dump/             # Database dump
│   └── gym_management.sql
├── .env                  # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## 🤝 Contributing

This is a backend assessment project. For questions or issues, please contact the development team.

## 📝 License

This project is created for assessment purposes.

---

**Built with Django REST Framework & PostgreSQL** 🚀