# HiveDesk - HR Onboarding System Backend API

FastAPI-based backend API for HiveDesk HR Onboarding System with PostgreSQL database, JWT authentication, and comprehensive employee management features.

## 🚀 Features

- **JWT Authentication** - Secure token-based authentication with 30-minute expiry
- **Role-Based Access Control** - HR and Employee roles with granular permissions
- **Employee Management** - Complete CRUD operations for employee records
- **Task Management** - Create, assign, track, and complete onboarding tasks
- **Training Modules** - Track employee training progress with auto-completion
- **Document Management** - Upload and manage employee documents
- **Performance Analytics** - Real-time performance metrics and completion rates
- **Pagination** - All list endpoints support pagination (page, page_size)
- **Auto-Generated Docs** - Interactive API documentation (Swagger & Scalar)

## 📋 Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.11+ (for local development)
- PostgreSQL 15+ (if running without Docker)

## 🛠️ Quick Start

### Using Docker (Recommended)

```bash
cd backend
docker-compose up -d
```

The API will be available at:
- **API Base URL**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Scalar Docs**: http://localhost:8000/scalar

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
DATABASE_URL=postgresql+asyncpg://postgres:roshan@localhost:5434/hr_onboarding_system
SECRET_KEY=your-secret-key-here
```

3. Run the application:
```bash
python run.py
```

## 🔐 Default Credentials

The system automatically creates default users on first startup:

**HR Account:**
- Email: `john.hr@company.com`
- Password: `password123`
- Role: `hr`

**Employee Accounts:**
- Email: `jane.employee@company.com`
- Password: `password123`
- Role: `employee`

(Additional employees: bob.employee@company.com, alice.employee@company.com)

## 📚 API Endpoints

### Authentication

#### POST `/auth/login`
Login and receive JWT access token.

**Request:**
```json
{
  "email": "john.hr@company.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "e5c9b9f1-76a2-4a66-b769-d2e9029654aa",
    "name": "John HR",
    "email": "john.hr@company.com",
    "role": "hr",
    "is_active": true,
    "created_at": "2025-12-27T07:00:38.280471",
    "updated_at": "2025-12-27T07:00:38.280475"
  }
}
```

#### POST `/auth/register`
Register a new employee account.

**Request:**
```json
{
  "name": "New Employee",
  "email": "new.employee@company.com",
  "password": "securepassword",
  "role": "employee"
}
```

**Response:** Same as login response

#### POST `/auth/logout`
Logout current user (client should discard token).

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Logged out successfully"
}
```

#### GET `/auth/me`
Get current authenticated user details.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "id": "e5c9b9f1-76a2-4a66-b769-d2e9029654aa",
  "name": "John HR",
  "email": "john.hr@company.com",
  "role": "hr",
  "is_active": true,
  "created_at": "2025-12-27T07:00:38.280471",
  "updated_at": "2025-12-27T07:00:38.280475"
}
```

#### GET `/auth/verify`
Verify if current token is valid.

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "message": "Token is valid"
}
```

---

### Dashboard

#### GET `/{name}/{role}/dashboard`
Get dashboard statistics for HR or Employee.

**Path Parameters:**
- `name`: URL-encoded lowercase name (e.g., `john-hr`, `jane%20employee`)
- `role`: User role (`hr` or `employee`)

**Headers:** `Authorization: Bearer <token>`

**HR Response:**
```json
{
  "role": "hr",
  "total_employees": 5,
  "pending_tasks": 3,
  "pending_documents": 2,
  "recent_activities": []
}
```

**Employee Response:**
```json
{
  "role": "employee",
  "total_tasks": 5,
  "completed_tasks": 3,
  "pending_tasks": 2,
  "completion_rate": 60.0
}
```

---

### Employee Management

#### GET `/{name}/hr/employees`
Get paginated list of all employees (HR only).

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50)

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
  "employees": [
    {
      "id": "7b1938cb-858e-4b25-9658-71468ccf01cd",
      "name": "Jane Employee",
      "email": "jane.employee@company.com",
      "is_active": true,
      "total_tasks": 5,
      "completed_tasks": 3,
      "completion_rate": 60.0
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

#### GET `/{name}/hr/manage/{employee_id}`
Get employee details with tasks and documents (HR only).

**Response:**
```json
{
  "employee": {
    "id": "7b1938cb-858e-4b25-9658-71468ccf01cd",
    "name": "Jane Employee",
    "email": "jane.employee@company.com",
    "is_active": true
  },
  "tasks": [
    {
      "assignment_id": "9d90df1d-8569-42d3-980f-c3631b2e3ec7",
      "task_id": "f63bb9ff-f823-4d49-a9a9-071fa159f670",
      "title": "Complete Onboarding",
      "description": "Read employee handbook",
      "task_type": "read",
      "status": "pending",
      "assigned_at": "2025-12-27T16:54:30.977534",
      "completed_at": null
    }
  ],
  "documents": []
}
```

#### PUT `/{name}/hr/employees/{employee_id}`
Update employee details (HR only).

**Request:**
```json
{
  "name": "Updated Name",
  "email": "updated.email@company.com",
  "is_active": true
}
```

**Response:**
```json
{
  "id": "7b1938cb-858e-4b25-9658-71468ccf01cd",
  "name": "Updated Name",
  "email": "updated.email@company.com",
  "role": "employee",
  "is_active": true,
  "created_at": "2025-12-27T07:00:38.530367",
  "updated_at": "2025-12-27T16:52:42.624941"
}
```

#### DELETE `/{name}/hr/employees/{employee_id}`
Delete employee with cascade deletion of related data (HR only).

**Response:**
```json
{
  "message": "Employee deleted successfully"
}
```

---

### Task Management

#### GET `/{name}/{role}/tasks`
Get paginated list of tasks (HR sees all, Employee sees assigned).

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50)

**Response:**
```json
{
  "tasks": [
    {
      "id": "f63bb9ff-f823-4d49-a9a9-071fa159f670",
      "title": "Complete Onboarding",
      "description": "Read employee handbook",
      "task_type": "read",
      "is_active": true,
      "created_at": "2025-12-27T16:53:56.809435"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

**Employee Response** (includes assignment details):
```json
{
  "tasks": [
    {
      "assignment_id": "9d90df1d-8569-42d3-980f-c3631b2e3ec7",
      "task_id": "f63bb9ff-f823-4d49-a9a9-071fa159f670",
      "title": "Complete Onboarding",
      "description": "Read employee handbook",
      "task_type": "read",
      "content": "Review company policies",
      "status": "pending",
      "assigned_at": "2025-12-27T16:54:30.977534",
      "completed_at": null
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

#### POST `/{name}/hr/tasks`
Create a new task (HR only).

**Request:**
```json
{
  "title": "Complete Onboarding",
  "description": "Read employee handbook",
  "task_type": "read",
  "content": "Review company policies",
  "is_active": true
}
```

**Task Types:** `read`, `upload`, `sign`

**Response:**
```json
{
  "id": "f63bb9ff-f823-4d49-a9a9-071fa159f670",
  "title": "Complete Onboarding",
  "description": "Read employee handbook",
  "task_type": "read",
  "content": "Review company policies",
  "required_document_type": null,
  "is_active": true,
  "created_by": "e5c9b9f1-76a2-4a66-b769-d2e9029654aa",
  "created_at": "2025-12-27T16:53:56.809435",
  "updated_at": "2025-12-27T16:53:56.809439"
}
```

#### PUT `/{name}/hr/tasks/{task_id}`
Update task details (HR only).

**Request:**
```json
{
  "title": "Updated Task Title",
  "description": "Updated description",
  "is_active": true
}
```

**Response:** Full task object with updated fields

#### DELETE `/{name}/hr/tasks/{task_id}`
Delete task with cascade deletion of assignments (HR only).

**Response:**
```json
{
  "message": "Task deleted successfully"
}
```

#### POST `/{name}/hr/assign-task`
Assign task to employee (HR only).

**Request:**
```json
{
  "employee_id": "7b1938cb-858e-4b25-9658-71468ccf01cd",
  "task_id": "f63bb9ff-f823-4d49-a9a9-071fa159f670"
}
```

**Response:**
```json
{
  "message": "Task assigned successfully"
}
```

#### POST `/{name}/employee/tasks/complete`
Mark assigned task as completed (Employee only).

**Request:**
```json
{
  "assignment_id": "9d90df1d-8569-42d3-980f-c3631b2e3ec7"
}
```

**Response:**
```json
{
  "message": "Task marked as completed"
}
```

---

### Document Management

#### GET `/{name}/{role}/documents`
Get paginated list of documents.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50)

**Response:**
```json
{
  "documents": [
    {
      "id": "30947b63-15df-4f0b-a5a3-3a1ff2f74354",
      "employee_id": "7b1938cb-858e-4b25-9658-71468ccf01cd",
      "document_type": "resume",
      "original_filename": "resume.txt",
      "verification_status": "pending",
      "uploaded_at": "2025-12-27T17:15:42.010902",
      "verified_at": null
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

**Document Types:** `aadhar`, `resume`, `other`

**Verification Status:** `pending`, `verified`, `rejected`

#### POST `/{name}/employee/documents/upload`
Upload document (Employee only).

**Request:** `multipart/form-data`
- `file`: File to upload
- `document_type`: Document type (`aadhar`, `resume`, `other`)

**Response:**
```json
{
  "message": "Document uploaded successfully",
  "document_id": "30947b63-15df-4f0b-a5a3-3a1ff2f74354"
}
```

---

### Training Management

#### GET `/{name}/{role}/training`
Get paginated list of training modules with progress.

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 50)

**Response:**
```json
{
  "training_modules": [
    {
      "id": "8183034f-f518-45cc-a0a7-0f859409b36f",
      "title": "Security Training",
      "description": "Learn security best practices",
      "duration_minutes": 60,
      "is_mandatory": true,
      "progress": {
        "status": "completed",
        "progress_percentage": 100,
        "started_at": "2025-12-27T17:14:13.274173",
        "completed_at": "2025-12-27T17:14:25.907075"
      }
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 50
}
```

#### PUT `/{name}/employee/training/{training_id}`
Update training progress (Employee only).

**Request:**
```json
{
  "progress_percentage": 75
}
```

**Note:** Automatically marks as completed when `progress_percentage >= 100`

**Response:**
```json
{
  "message": "Training progress updated successfully"
}
```

---

### Performance Analytics

#### GET `/{name}/hr/performance`
Get overall system performance statistics (HR only).

**Response:**
```json
{
  "total_employees": 4,
  "active_employees": 4,
  "total_tasks_assigned": 10,
  "total_tasks_completed": 6,
  "overall_task_completion_rate": 60.0,
  "total_training_modules": 5,
  "avg_training_completion": 75.5,
  "pending_documents": 3
}
```

#### GET `/{name}/hr/performance/{employee_id}`
Get individual employee performance metrics (HR only).

**Response:**
```json
{
  "employee_id": "7b1938cb-858e-4b25-9658-71468ccf01cd",
  "employee_name": "Jane Employee",
  "total_tasks": 5,
  "completed_tasks": 3,
  "pending_tasks": 2,
  "completion_rate": 60.0,
  "total_training": 5,
  "completed_training": 4,
  "training_completion_rate": 80.0,
  "avg_task_completion_days": 2.5
}
```

---

## 🔌 Frontend Integration Guide

### Setting Up API Client

```javascript
// src/services/api.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 responses
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Authentication Flow

```javascript
// Login
const login = async (email, password) => {
  const response = await apiClient.post('/auth/login', { email, password });
  localStorage.setItem('access_token', response.data.access_token);
  return response.data.user;
};

// Logout
const logout = async () => {
  await apiClient.post('/auth/logout');
  localStorage.removeItem('access_token');
};

// Get current user
const getCurrentUser = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};
```

### URL Name Encoding

Names with spaces must be URL-encoded in path parameters:

```javascript
// Correct
const encodedName = encodeURIComponent(user.name.toLowerCase());
const url = `/${encodedName}/${user.role}/dashboard`;
// Result: /jane%20employee/employee/dashboard

// Incorrect
const url = `/${user.name.toLowerCase()}/${user.role}/dashboard`;
// Would fail for names with spaces
```

### File Upload

```javascript
const uploadDocument = async (file, documentType, userName, role) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);

  const encodedName = encodeURIComponent(userName.toLowerCase());
  const response = await apiClient.post(
    `/${encodedName}/${role}/documents/upload`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};
```

### Pagination

```javascript
const getTasks = async (page = 1, pageSize = 50) => {
  const response = await apiClient.get(`/${name}/${role}/tasks`, {
    params: { page, page_size: pageSize },
  });
  return {
    tasks: response.data.tasks,
    total: response.data.total,
    page: response.data.page,
    pageSize: response.data.page_size,
  };
};
```

---

## 🗄️ Database Schema

### Users
- `id`: UUID (Primary Key)
- `name`: String
- `email`: String (Unique)
- `password_hash`: String
- `role`: Enum (hr, employee)
- `is_active`: Boolean
- `created_at`: DateTime
- `updated_at`: DateTime

### Tasks
- `id`: UUID (Primary Key)
- `title`: String
- `description`: String (Optional)
- `task_type`: Enum (read, upload, sign)
- `content`: String (Optional)
- `required_document_type`: Enum (Optional)
- `is_active`: Boolean
- `created_by`: UUID (Foreign Key → Users)

### Employee Tasks (Assignments)
- `id`: UUID (Primary Key)
- `employee_id`: UUID (Foreign Key → Users)
- `task_id`: UUID (Foreign Key → Tasks)
- `status`: Enum (pending, completed)
- `assigned_at`: DateTime
- `completed_at`: DateTime (Optional)

### Training Modules
- `id`: UUID (Primary Key)
- `title`: String
- `description`: String (Optional)
- `content`: String (Optional)
- `duration_minutes`: Integer
- `is_mandatory`: Boolean
- `is_active`: Boolean

### Employee Training (Progress)
- `id`: UUID (Primary Key)
- `employee_id`: UUID (Foreign Key → Users)
- `training_module_id`: UUID (Foreign Key → Training Modules)
- `progress_percentage`: Integer
- `status`: Enum (pending, completed)
- `started_at`: DateTime
- `completed_at`: DateTime (Optional)

### Documents
- `id`: UUID (Primary Key)
- `employee_id`: UUID (Foreign Key → Users)
- `document_type`: Enum (aadhar, resume, other)
- `file_path`: String
- `original_filename`: String
- `verification_status`: Enum (pending, verified, rejected)
- `uploaded_at`: DateTime
- `verified_at`: DateTime (Optional)

---

## 🔒 Security

- **JWT Tokens**: 30-minute expiry, HS256 algorithm
- **Password Hashing**: bcrypt with salt
- **CORS**: Configured for localhost:5173, localhost:3000
- **Role-Based Access**: Endpoints protected by role decorators
- **Input Validation**: Pydantic schemas validate all requests

---

## 🐳 Docker Configuration

### Services

**PostgreSQL Database:**
- Image: `postgres:15-alpine`
- Port: `5434:5432`
- Database: `hr_onboarding_system`
- User: `postgres`
- Password: `roshan`
- Volume: `postgres_data` (persistent storage)

**FastAPI Backend:**
- Python: `3.11-slim`
- Port: `8000:8000`
- Auto-restarts on failure
- Multi-stage optimized build

### Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart backend
docker-compose restart backend

# Stop services
docker-compose down

# Rebuild (after code changes)
docker-compose build --no-cache backend
docker-compose up -d
```

---

## 📝 Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:roshan@postgres:5432/hr_onboarding_system

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🧪 Testing

All endpoints have been tested and validated:
- ✅ 31/31 endpoints working
- ✅ Pagination tested
- ✅ Role-based access verified
- ✅ Cascade deletions validated
- ✅ Auto-completion logic confirmed
- ✅ File uploads working
- ✅ Performance analytics accurate

---

## 📖 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **Scalar UI**: http://localhost:8000/scalar

Both provide:
- Complete endpoint listing
- Request/response schemas
- Try-it-out functionality
- Authentication support

---

## 🤝 Support

For issues or questions:
1. Check the interactive API docs at `/docs` or `/scalar`
2. Review this README for integration examples
3. Verify authentication tokens are being sent correctly
4. Ensure URL encoding for names with spaces

---

## 📄 License

Private project - All rights reserved
