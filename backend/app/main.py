"""
FastAPI HR Onboarding System - Async Main Application
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import HTMLResponse
# from scalar_fastapi import get_scalar_api_reference
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from typing import Optional
from datetime import datetime, timedelta
import aiofiles
from pathlib import Path

from .database import create_db_and_tables, get_async_session
from .models import (
    UserModel, TaskModel, EmployeeTaskModel, DocumentModel,
    TrainingModuleModel, EmployeeTrainingModel
)
from .schemas import (
    UserCreateSchema, UserResponseSchema, UserLoginSchema, UserLoginResponseSchema,
    UserUpdateSchema, TaskCreateSchema, TaskUpdateSchema, TaskResponseSchema,
    DocumentUploadResponseSchema,
    DashboardHRResponseSchema, DashboardEmployeeResponseSchema,
    EmployeeListResponseSchema, EmployeeManageResponseSchema,
    TaskListResponseSchema, HRTaskListResponseSchema,
    DocumentListResponseSchema, TrainingListResponseSchema,
    HRTrainingListResponseSchema, MessageResponseSchema,
    AssignTaskResponseSchema, EmployeePerformanceSchema,
    OverallPerformanceSchema, TrainingProgressUpdateSchema
)
from .core.enums import UserRole, TaskStatus, VerificationStatus, DocumentType
from .auth import (
    authenticate_user, create_access_token, get_current_user, 
    require_role, verify_user_access, get_password_hash
)

# Create FastAPI app
app = FastAPI(
    title="HR Onboarding System",
    version="2.0.0",
    description="Async HR Onboarding System with FastAPI and SQLModel"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Security
security = HTTPBearer()


@app.on_event("startup")
async def on_startup():
    """Create database tables and default users on startup"""
    from .models.user import UserModel
    from .core.enums import UserRole
    from .auth import get_password_hash
    from .database import AsyncSessionLocal
    
    # Create tables
    await create_db_and_tables()
    
    # Create default users if they don't exist
    async with AsyncSessionLocal() as session:
        # Check if HR user exists
        hr_stmt = select(UserModel).where(UserModel.email == "john.hr@company.com")
        result = await session.execute(hr_stmt)
        hr_exists = result.scalar_one_or_none()
        
        if not hr_exists:
            print("\n" + "="*50)
            print("🔧 Creating default users...")
            print("="*50)
            
            # Create HR user
            hr_user = UserModel(
                name="John HR",
                email="john.hr@company.com",
                password_hash=get_password_hash("password123"),
                role=UserRole.HR
            )
            session.add(hr_user)
            
            # Create sample employees
            employees = [
                ("Jane Employee", "jane.employee@company.com"),
                ("Bob Employee", "bob.employee@company.com"),
                ("Alice Employee", "alice.employee@company.com")
            ]
            
            for name, email in employees:
                employee = UserModel(
                    name=name,
                    email=email,
                    password_hash=get_password_hash("password123"),
                    role=UserRole.EMPLOYEE
                )
                session.add(employee)
            
            await session.commit()
            print("\n✅ Default users created successfully!")
            print("\n📋 Test Credentials:")
            print("   HR User:")
            print("   └─ Email: john.hr@company.com")
            print("   └─ Password: password123")
            print("\n   Employees:")
            print("   └─ jane.employee@company.com / password123")
            print("   └─ bob.employee@company.com / password123")
            print("   └─ alice.employee@company.com / password123")
            print("="*50 + "\n")
        else:
            print("✓ Default users already exist, skipping creation.")


# Scalar API Documentation (temporarily disabled)
# @app.get("/scalar", include_in_schema=False, response_class=HTMLResponse)
# def get_scalar_docs():
#     """Scalar API documentation endpoint"""
#     return get_scalar_api_reference(
#         openapi_url=app.openapi_url,
#         title="HR Onboarding System API",
#     )


# Authentication endpoints
@app.post("/auth/login", response_model=UserLoginResponseSchema)
async def login(
    login_data: UserLoginSchema,
    session: AsyncSession = Depends(get_async_session)
):
    """Login endpoint"""
    user = await authenticate_user(session, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return UserLoginResponseSchema(
        access_token=access_token,
        token_type="bearer",
        user=UserResponseSchema.from_orm(user)
    )


@app.post("/auth/register", response_model=UserResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def register_user(
    user_data: UserCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Register new user (HR only)"""
    # Check if user already exists
    statement = select(UserModel).where(UserModel.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = UserModel(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        is_active=user_data.is_active
    )
    
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    
    return UserResponseSchema.from_orm(db_user)


@app.post("/auth/logout", response_model=MessageResponseSchema)
async def logout(
    current_user: UserModel = Depends(get_current_user)
):
    """Logout endpoint - client should discard token"""
    return {"message": "Logged out successfully"}


@app.get("/auth/me", response_model=UserResponseSchema)
async def get_current_user_info(
    current_user: UserModel = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponseSchema.from_orm(current_user)


@app.get("/auth/verify", response_model=MessageResponseSchema)
async def verify_token(
    current_user: UserModel = Depends(get_current_user)
):
    """Verify if token is valid"""
    return {"message": "Token is valid"}


# Dashboard endpoints
@app.get("/{name}/{role}/dashboard")
async def get_dashboard(
    name: str,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get dashboard data for HR or Employee"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if role.lower() == "hr":
        # HR Dashboard
        employees_stmt = select(UserModel).where(UserModel.role == UserRole.EMPLOYEE)
        employees_result = await session.execute(employees_stmt)
        total_employees = employees_result.scalars().all()
        
        pending_tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.status == TaskStatus.PENDING)
        pending_tasks_result = await session.execute(pending_tasks_stmt)
        pending_tasks = pending_tasks_result.scalars().all()
        
        pending_docs_stmt = select(DocumentModel).where(DocumentModel.verification_status == VerificationStatus.PENDING)
        pending_docs_result = await session.execute(pending_docs_stmt)
        pending_documents = pending_docs_result.scalars().all()
        
        return {
            "role": "hr",
            "total_employees": len(total_employees),
            "pending_tasks": len(pending_tasks),
            "pending_documents": len(pending_documents),
            "recent_activities": []
        }
    
    elif role.lower() == "employee":
        # Employee Dashboard
        user_tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == current_user.id)
        user_tasks_result = await session.execute(user_tasks_stmt)
        user_tasks = user_tasks_result.scalars().all()
        
        completed_tasks = [task for task in user_tasks if task.status == TaskStatus.COMPLETED]
        pending_tasks = [task for task in user_tasks if task.status == TaskStatus.PENDING]
        
        return {
            "role": "employee",
            "total_tasks": len(user_tasks),
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
            "completion_rate": len(completed_tasks) / len(user_tasks) * 100 if user_tasks else 0
        }


@app.get("/{name}/{role}/employees", response_model=EmployeeListResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def get_all_employees(
    name: str,
    role: str,
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all employees (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Get total count
    count_stmt = select(func.count()).select_from(UserModel).where(UserModel.role == UserRole.EMPLOYEE)
    total_result = await session.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated employees
    offset = (page - 1) * page_size
    employees_stmt = select(UserModel).where(UserModel.role == UserRole.EMPLOYEE).offset(offset).limit(page_size)
    employees_result = await session.execute(employees_stmt)
    employees = employees_result.scalars().all()
    
    employee_data = []
    for employee in employees:
        # Get task statistics
        tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == employee.id)
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()
        
        completed = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
        total = len(tasks)
        
        employee_data.append({
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "is_active": employee.is_active,
            "total_tasks": total,
            "completed_tasks": completed,
            "completion_rate": completed / total * 100 if total > 0 else 0
        })
    
    return {
        "employees": employee_data,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@app.get("/{name}/{role}/manage/{employee_id}", response_model=EmployeeManageResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def manage_employee(
    name: str,
    role: str,
    employee_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Manage specific employee (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find employee by ID (secure)
    employee = await session.get(UserModel, employee_id)
    
    if not employee or employee.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    # Get employee's tasks
    tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == employee.id)
    tasks_result = await session.execute(tasks_stmt)
    tasks = tasks_result.scalars().all()
    
    # Get employee's documents
    docs_stmt = select(DocumentModel).where(DocumentModel.employee_id == employee.id)
    docs_result = await session.execute(docs_stmt)
    documents = docs_result.scalars().all()
    
    return {
        "employee": {
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "is_active": employee.is_active
        },
        "tasks": [
            {
                "id": task.id,
                "task_id": task.task_id,
                "status": task.status.value,
                "assigned_at": task.assigned_at,
                "completed_at": task.completed_at
            } for task in tasks
        ],
        "documents": [
            {
                "id": doc.id,
                "document_type": doc.document_type.value,
                "original_filename": doc.original_filename,
                "verification_status": doc.verification_status.value,
                "uploaded_at": doc.uploaded_at
            } for doc in documents
        ]
    }


@app.put("/{name}/{role}/employees/{employee_id}", response_model=UserResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def update_employee(
    name: str,
    role: str,
    employee_id: str,
    update_data: UserUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Update employee information (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find employee
    employee = await session.get(UserModel, employee_id)
    if not employee or employee.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    # Update fields
    if update_data.name is not None:
        employee.name = update_data.name
    if update_data.email is not None:
        # Check email uniqueness
        email_stmt = select(UserModel).where(UserModel.email == update_data.email, UserModel.id != employee_id)
        email_result = await session.execute(email_stmt)
        if email_result.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        employee.email = update_data.email
    if update_data.is_active is not None:
        employee.is_active = update_data.is_active
    
    employee.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(employee)
    
    return UserResponseSchema.from_orm(employee)


@app.delete("/{name}/{role}/employees/{employee_id}", response_model=MessageResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def delete_employee(
    name: str,
    role: str,
    employee_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete employee (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find employee
    employee = await session.get(UserModel, employee_id)
    if not employee or employee.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    # Delete related records first (cascade)
    # Delete employee tasks
    tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == employee_id)
    tasks_result = await session.execute(tasks_stmt)
    tasks = tasks_result.scalars().all()
    for task in tasks:
        await session.delete(task)
    
    # Delete employee documents
    docs_stmt = select(DocumentModel).where(DocumentModel.employee_id == employee_id)
    docs_result = await session.execute(docs_stmt)
    documents = docs_result.scalars().all()
    for doc in documents:
        await session.delete(doc)
    
    # Delete employee training
    training_stmt = select(EmployeeTrainingModel).where(EmployeeTrainingModel.employee_id == employee_id)
    training_result = await session.execute(training_stmt)
    trainings = training_result.scalars().all()
    for training in trainings:
        await session.delete(training)
    
    # Delete employee
    await session.delete(employee)
    await session.commit()
    
    return {"message": "Employee deleted successfully"}


class AssignTaskRequest(BaseModel):
    employee_id: str
    task_id: str

@app.post("/{name}/{role}/assign-task", response_model=MessageResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def assign_task(
    name: str,
    role: str,
    request_data: AssignTaskRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Assign task to employee (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Check if assignment already exists
    existing_stmt = select(EmployeeTaskModel).where(
        EmployeeTaskModel.employee_id == request_data.employee_id,
        EmployeeTaskModel.task_id == request_data.task_id
    )
    existing_result = await session.execute(existing_stmt)
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Task already assigned")
    
    # Create assignment
    assignment = EmployeeTaskModel(
        employee_id=request_data.employee_id,
        task_id=request_data.task_id,
        assigned_by=current_user.id
    )
    
    session.add(assignment)
    await session.commit()
    
    return {"message": "Task assigned successfully"}


@app.get("/{name}/{role}/documents")
async def get_documents(
    name: str,
    role: str,
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get documents - HR sees all, Employee sees their own"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if role.lower() == "hr":
        # Get total count for HR
        count_stmt = select(func.count()).select_from(DocumentModel)
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # HR sees all documents with pagination
        offset = (page - 1) * page_size
        docs_stmt = select(DocumentModel).offset(offset).limit(page_size)
        docs_result = await session.execute(docs_stmt)
        documents = docs_result.scalars().all()
    else:
        # Get total count for Employee
        count_stmt = select(func.count()).select_from(DocumentModel).where(DocumentModel.employee_id == current_user.id)
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Employee sees only their documents with pagination
        offset = (page - 1) * page_size
        docs_stmt = select(DocumentModel).where(DocumentModel.employee_id == current_user.id).offset(offset).limit(page_size)
        docs_result = await session.execute(docs_stmt)
        documents = docs_result.scalars().all()
    
    return {
        "documents": [
            {
                "id": doc.id,
                "employee_id": doc.employee_id,
                "document_type": doc.document_type.value,
                "original_filename": doc.original_filename,
                "verification_status": doc.verification_status.value,
                "uploaded_at": doc.uploaded_at,
                "verified_at": doc.verified_at
            } for doc in documents
        ],
        "total": total,
        "page": page,
        "page_size": page_size
    }


@app.post("/{name}/{role}/documents/upload", response_model=DocumentUploadResponseSchema)
async def upload_document(
    name: str,
    role: str,
    file: UploadFile = File(...),
    document_type: str = Form(...),
    task_id: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Upload document"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Validate document type
    try:
        doc_type = DocumentType(document_type.lower())
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document type")
    
    # Create file path
    filename = f"{current_user.id}_{doc_type.value}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    # Save file asynchronously
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="File upload failed")
    
    # Save document metadata
    document = DocumentModel(
        employee_id=current_user.id,
        document_type=doc_type,
        original_filename=file.filename,
        file_path=str(file_path),
        file_size=file.size,
        mime_type=file.content_type,
        task_id=task_id
    )
    
    session.add(document)
    await session.commit()
    await session.refresh(document)
    
    return DocumentUploadResponseSchema(
        message="Document uploaded successfully",
        document_id=document.id
    )


@app.get("/{name}/{role}/tasks")
async def get_tasks(
    name: str,
    role: str,
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get tasks - HR sees all tasks, Employee sees assigned tasks"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    if role.lower() == "hr":
        # Get total count
        count_stmt = select(func.count()).select_from(TaskModel)
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # HR sees all tasks with pagination
        offset = (page - 1) * page_size
        tasks_stmt = select(TaskModel).offset(offset).limit(page_size)
        tasks_result = await session.execute(tasks_stmt)
        tasks = tasks_result.scalars().all()
        
        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "is_active": task.is_active,
                    "created_at": task.created_at
                } for task in tasks
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    else:
        # Employee sees assigned tasks
        # Get total count
        count_stmt = select(func.count()).select_from(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == current_user.id)
        total_result = await session.execute(count_stmt)
        total = total_result.scalar()
        
        # Get paginated tasks
        offset = (page - 1) * page_size
        employee_tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == current_user.id).offset(offset).limit(page_size)
        employee_tasks_result = await session.execute(employee_tasks_stmt)
        employee_tasks = employee_tasks_result.scalars().all()
        
        task_data = []
        for emp_task in employee_tasks:
            task = await session.get(TaskModel, emp_task.task_id)
            if task:
                task_data.append({
                    "assignment_id": emp_task.id,
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "task_type": task.task_type.value,
                    "content": task.content,
                    "status": emp_task.status.value,
                    "assigned_at": emp_task.assigned_at,
                    "completed_at": emp_task.completed_at
                })
        
        return {
            "tasks": task_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }


@app.post("/{name}/{role}/tasks", response_model=TaskResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def create_task(
    name: str,
    role: str,
    task_data: TaskCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Create new task (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Create task
    new_task = TaskModel(
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        content=task_data.content,
        required_document_type=task_data.required_document_type,
        is_active=task_data.is_active,
        created_by=current_user.id
    )
    
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    
    return TaskResponseSchema.from_orm(new_task)


@app.put("/{name}/{role}/tasks/{task_id}", response_model=TaskResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def update_task(
    name: str,
    role: str,
    task_id: str,
    update_data: TaskUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Update task (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find task
    task = await session.get(TaskModel, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Update fields
    if update_data.title is not None:
        task.title = update_data.title
    if update_data.description is not None:
        task.description = update_data.description
    if update_data.content is not None:
        task.content = update_data.content
    if update_data.is_active is not None:
        task.is_active = update_data.is_active
    
    task.updated_at = datetime.utcnow()
    await session.commit()
    await session.refresh(task)
    
    return TaskResponseSchema.from_orm(task)


@app.delete("/{name}/{role}/tasks/{task_id}", response_model=MessageResponseSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def delete_task(
    name: str,
    role: str,
    task_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Delete task (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find task
    task = await session.get(TaskModel, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    # Delete task assignments first
    assignments_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.task_id == task_id)
    assignments_result = await session.execute(assignments_stmt)
    assignments = assignments_result.scalars().all()
    for assignment in assignments:
        await session.delete(assignment)
    
    # Delete task
    await session.delete(task)
    await session.commit()
    
    return {"message": "Task deleted successfully"}


class CompleteTaskRequest(BaseModel):
    assignment_id: str

@app.post("/{name}/{role}/tasks/complete", response_model=MessageResponseSchema)
async def complete_task(
    name: str,
    role: str,
    request_data: CompleteTaskRequest,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Mark task as completed"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Find task assignment
    assignment = await session.get(EmployeeTaskModel, request_data.assignment_id)
    if not assignment or assignment.employee_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task assignment not found")
    
    # Update status
    assignment.status = TaskStatus.COMPLETED
    assignment.completed_at = datetime.utcnow()
    
    session.add(assignment)
    await session.commit()
    
    return {"message": "Task marked as completed"}


@app.get("/{name}/{role}/training")
async def get_training_modules(
    name: str,
    role: str,
    page: int = 1,
    page_size: int = 50,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get training modules"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Get total count
    count_stmt = select(func.count()).select_from(TrainingModuleModel).where(TrainingModuleModel.is_active)
    total_result = await session.execute(count_stmt)
    total = total_result.scalar()
    
    # Get paginated modules
    offset = (page - 1) * page_size
    modules_stmt = select(TrainingModuleModel).where(TrainingModuleModel.is_active).offset(offset).limit(page_size)
    modules_result = await session.execute(modules_stmt)
    modules = modules_result.scalars().all()
    
    if role.lower() == "employee":
        # Get employee's progress for each module
        progress_data = []
        for module in modules:
            progress_stmt = select(EmployeeTrainingModel).where(
                EmployeeTrainingModel.employee_id == current_user.id,
                EmployeeTrainingModel.training_module_id == module.id
            )
            progress_result = await session.execute(progress_stmt)
            progress = progress_result.scalar_one_or_none()
            
            progress_data.append({
                "id": module.id,
                "title": module.title,
                "description": module.description,
                "duration_minutes": module.duration_minutes,
                "is_mandatory": module.is_mandatory,
                "progress": {
                    "status": progress.status.value if progress else "pending",
                    "progress_percentage": progress.progress_percentage if progress else 0,
                    "started_at": progress.started_at if progress else None,
                    "completed_at": progress.completed_at if progress else None
                }
            })
        
        return {
            "training_modules": progress_data,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    else:
        # HR sees all modules
        return {
            "training_modules": [
                {
                    "id": module.id,
                    "title": module.title,
                    "description": module.description,
                    "content": module.content,
                    "duration_minutes": module.duration_minutes,
                    "is_mandatory": module.is_mandatory,
                    "created_at": module.created_at
                } for module in modules
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }


@app.put("/{name}/{role}/training/{training_id}", response_model=MessageResponseSchema)
async def update_training_progress(
    name: str,
    role: str,
    training_id: str,
    progress_data: TrainingProgressUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Update training progress"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # For employees, find or create training record
    progress_stmt = select(EmployeeTrainingModel).where(
        EmployeeTrainingModel.employee_id == current_user.id,
        EmployeeTrainingModel.training_module_id == training_id
    )
    progress_result = await session.execute(progress_stmt)
    progress = progress_result.scalar_one_or_none()
    
    if not progress:
        # Create new progress record
        initial_status = TaskStatus.COMPLETED if progress_data.progress_percentage >= 100 else TaskStatus.PENDING
        progress = EmployeeTrainingModel(
            employee_id=current_user.id,
            training_module_id=training_id,
            progress_percentage=progress_data.progress_percentage,
            status=initial_status,
            started_at=datetime.utcnow()
        )
        if progress_data.progress_percentage >= 100:
            progress.completed_at = datetime.utcnow()
        session.add(progress)
    else:
        # Update existing record
        progress.progress_percentage = progress_data.progress_percentage
        
        # Mark as completed if 100%
        if progress_data.progress_percentage >= 100:
            progress.status = TaskStatus.COMPLETED
            progress.completed_at = datetime.utcnow()
        else:
            progress.status = TaskStatus.PENDING
    
    await session.commit()
    return {"message": "Training progress updated successfully"}


@app.get("/{name}/{role}/performance", response_model=OverallPerformanceSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def get_overall_performance(
    name: str,
    role: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get overall performance statistics (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Total employees
    total_emp_stmt = select(func.count()).select_from(UserModel).where(UserModel.role == UserRole.EMPLOYEE)
    total_emp_result = await session.execute(total_emp_stmt)
    total_employees = total_emp_result.scalar()
    
    # Active employees
    active_emp_stmt = select(func.count()).select_from(UserModel).where(
        UserModel.role == UserRole.EMPLOYEE,
        UserModel.is_active == True
    )
    active_emp_result = await session.execute(active_emp_stmt)
    active_employees = active_emp_result.scalar()
    
    # Total tasks assigned
    total_tasks_stmt = select(func.count()).select_from(EmployeeTaskModel)
    total_tasks_result = await session.execute(total_tasks_stmt)
    total_tasks_assigned = total_tasks_result.scalar()
    
    # Total tasks completed
    completed_tasks_stmt = select(func.count()).select_from(EmployeeTaskModel).where(
        EmployeeTaskModel.status == TaskStatus.COMPLETED
    )
    completed_tasks_result = await session.execute(completed_tasks_stmt)
    total_tasks_completed = completed_tasks_result.scalar()
    
    # Overall task completion rate
    overall_task_completion_rate = (total_tasks_completed / total_tasks_assigned * 100) if total_tasks_assigned > 0 else 0
    
    # Total training modules
    total_training_stmt = select(func.count()).select_from(TrainingModuleModel).where(TrainingModuleModel.is_active == True)
    total_training_result = await session.execute(total_training_stmt)
    total_training_modules = total_training_result.scalar()
    
    # Average training completion
    completed_training_stmt = select(func.count()).select_from(EmployeeTrainingModel).where(
        EmployeeTrainingModel.status == TaskStatus.COMPLETED
    )
    completed_training_result = await session.execute(completed_training_stmt)
    completed_training_count = completed_training_result.scalar()
    
    total_training_assignments_stmt = select(func.count()).select_from(EmployeeTrainingModel)
    total_training_assignments_result = await session.execute(total_training_assignments_stmt)
    total_training_assignments = total_training_assignments_result.scalar()
    
    avg_training_completion = (completed_training_count / total_training_assignments * 100) if total_training_assignments > 0 else 0
    
    # Pending documents
    pending_docs_stmt = select(func.count()).select_from(DocumentModel).where(
        DocumentModel.verification_status == VerificationStatus.PENDING
    )
    pending_docs_result = await session.execute(pending_docs_stmt)
    pending_documents = pending_docs_result.scalar()
    
    return OverallPerformanceSchema(
        total_employees=total_employees,
        active_employees=active_employees,
        total_tasks_assigned=total_tasks_assigned,
        total_tasks_completed=total_tasks_completed,
        overall_task_completion_rate=overall_task_completion_rate,
        total_training_modules=total_training_modules,
        avg_training_completion=avg_training_completion,
        pending_documents=pending_documents
    )


@app.get("/{name}/{role}/performance/{employee_id}", response_model=EmployeePerformanceSchema, dependencies=[Depends(require_role(UserRole.HR))])
async def get_employee_performance(
    name: str,
    role: str,
    employee_id: str,
    session: AsyncSession = Depends(get_async_session),
    current_user: UserModel = Depends(get_current_user)
):
    """Get individual employee performance (HR only)"""
    if not verify_user_access(name, role, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Get employee
    employee = await session.get(UserModel, employee_id)
    if not employee or employee.role != UserRole.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    
    # Get task statistics
    tasks_stmt = select(EmployeeTaskModel).where(EmployeeTaskModel.employee_id == employee_id)
    tasks_result = await session.execute(tasks_stmt)
    tasks = tasks_result.scalars().all()
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.status == TaskStatus.COMPLETED])
    pending_tasks = total_tasks - completed_tasks
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Calculate average task completion time
    completed_with_dates = [t for t in tasks if t.status == TaskStatus.COMPLETED and t.completed_at and t.assigned_at]
    if completed_with_dates:
        total_days = sum([(t.completed_at - t.assigned_at).days for t in completed_with_dates])
        avg_task_completion_days = total_days / len(completed_with_dates)
    else:
        avg_task_completion_days = None
    
    # Get training statistics
    training_stmt = select(EmployeeTrainingModel).where(EmployeeTrainingModel.employee_id == employee_id)
    training_result = await session.execute(training_stmt)
    trainings = training_result.scalars().all()
    
    total_training = len(trainings)
    completed_training = len([t for t in trainings if t.status == TaskStatus.COMPLETED])
    training_completion_rate = (completed_training / total_training * 100) if total_training > 0 else 0
    
    return EmployeePerformanceSchema(
        employee_id=employee.id,
        employee_name=employee.name,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        completion_rate=completion_rate,
        total_training=total_training,
        completed_training=completed_training,
        training_completion_rate=training_completion_rate,
        avg_task_completion_days=avg_task_completion_days
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)