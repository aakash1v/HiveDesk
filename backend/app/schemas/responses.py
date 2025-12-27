"""
Response schemas for API endpoints
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..core.enums import TaskStatus, VerificationStatus


# Dashboard Schemas
class DashboardHRResponseSchema(BaseModel):
    """HR Dashboard response"""
    role: str
    total_employees: int
    pending_tasks: int
    pending_documents: int
    recent_activities: List[dict] = []


class DashboardEmployeeResponseSchema(BaseModel):
    """Employee Dashboard response"""
    role: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float


# Employee Management Schemas
class EmployeeStatsSchema(BaseModel):
    """Employee with task statistics"""
    id: str
    name: str
    email: str
    is_active: bool
    total_tasks: int
    completed_tasks: int
    completion_rate: float


class EmployeeListResponseSchema(BaseModel):
    """List of employees with pagination"""
    employees: List[EmployeeStatsSchema]
    total: int
    page: int
    page_size: int


class EmployeeDetailSchema(BaseModel):
    """Employee basic info"""
    id: str
    name: str
    email: str
    is_active: bool


class TaskAssignmentSchema(BaseModel):
    """Task assignment info"""
    id: str
    task_id: str
    status: str
    assigned_at: datetime
    completed_at: Optional[datetime]


class DocumentInfoSchema(BaseModel):
    """Document basic info"""
    id: str
    document_type: str
    original_filename: str
    verification_status: str
    uploaded_at: datetime


class EmployeeManageResponseSchema(BaseModel):
    """Detailed employee management response"""
    employee: EmployeeDetailSchema
    tasks: List[TaskAssignmentSchema]
    documents: List[DocumentInfoSchema]


# Task Schemas
class TaskDetailSchema(BaseModel):
    """Task detail for employee"""
    assignment_id: str
    task_id: str
    title: str
    description: Optional[str]
    task_type: str
    content: Optional[str]
    status: str
    assigned_at: datetime
    completed_at: Optional[datetime]


class TaskListResponseSchema(BaseModel):
    """Task list response"""
    tasks: List[TaskDetailSchema]
    total: int
    page: int = 1
    page_size: int = 50


class TaskBasicSchema(BaseModel):
    """Basic task info for HR"""
    id: str
    title: str
    description: Optional[str]
    task_type: str
    is_active: bool
    created_at: datetime


class HRTaskListResponseSchema(BaseModel):
    """HR task list response"""
    tasks: List[TaskBasicSchema]
    total: int


# Document Schemas
class DocumentListItemSchema(BaseModel):
    """Document in list view"""
    id: str
    employee_id: str
    document_type: str
    original_filename: str
    verification_status: str
    uploaded_at: datetime
    verified_at: Optional[datetime]


class DocumentListResponseSchema(BaseModel):
    """Document list response with pagination"""
    documents: List[DocumentListItemSchema]
    total: int
    page: int
    page_size: int


# Training Schemas
class TrainingProgressSchema(BaseModel):
    """Training progress for employee"""
    status: str
    progress_percentage: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class TrainingModuleEmployeeSchema(BaseModel):
    """Training module with employee progress"""
    id: str
    title: str
    description: Optional[str]
    duration_minutes: Optional[int]
    is_mandatory: bool
    progress: TrainingProgressSchema


class TrainingModuleHRSchema(BaseModel):
    """Training module for HR view"""
    id: str
    title: str
    description: Optional[str]
    content: str
    duration_minutes: Optional[int]
    is_mandatory: bool
    created_at: datetime


class TrainingListResponseSchema(BaseModel):
    """Training list response"""
    training_modules: List[TrainingModuleEmployeeSchema]
    total: int


class HRTrainingListResponseSchema(BaseModel):
    """HR training list response"""
    training_modules: List[TrainingModuleHRSchema]
    total: int


# Generic Response Schemas
class MessageResponseSchema(BaseModel):
    """Generic message response"""
    message: str


class AssignTaskResponseSchema(BaseModel):
    """Task assignment response"""
    message: str
    assignment_id: Optional[str] = None


# Performance Schemas
class EmployeePerformanceSchema(BaseModel):
    """Individual employee performance metrics"""
    employee_id: str
    employee_name: str
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float
    total_training: int
    completed_training: int
    training_completion_rate: float
    avg_task_completion_days: Optional[float] = None


class OverallPerformanceSchema(BaseModel):
    """Overall system performance metrics"""
    total_employees: int
    active_employees: int
    total_tasks_assigned: int
    total_tasks_completed: int
    overall_task_completion_rate: float
    total_training_modules: int
    avg_training_completion: float
    pending_documents: int


# Training Update Schema
class TrainingProgressUpdateSchema(BaseModel):
    """Update training progress"""
    progress_percentage: int
    status: Optional[str] = None
