"""
Pydantic schemas for HR Onboarding System
"""
from .user import (
    UserBaseSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserResponseSchema,
    UserLoginSchema,
    UserLoginResponseSchema
)
from .task import (
    TaskBaseSchema,
    TaskCreateSchema,
    TaskUpdateSchema,
    TaskResponseSchema,
    EmployeeTaskBaseSchema,
    EmployeeTaskCreateSchema,
    EmployeeTaskUpdateSchema,
    EmployeeTaskResponseSchema,
    EmployeeTaskWithDetailsSchema
)
from .document import (
    DocumentBaseSchema,
    DocumentCreateSchema,
    DocumentUpdateSchema,
    DocumentResponseSchema,
    DocumentUploadResponseSchema
)
from .responses import (
    DashboardHRResponseSchema,
    DashboardEmployeeResponseSchema,
    EmployeeListResponseSchema,
    EmployeeManageResponseSchema,
    TaskListResponseSchema,
    HRTaskListResponseSchema,
    DocumentListResponseSchema,
    TrainingListResponseSchema,
    HRTrainingListResponseSchema,
    MessageResponseSchema,
    AssignTaskResponseSchema,
    EmployeePerformanceSchema,
    OverallPerformanceSchema,
    TrainingProgressUpdateSchema
)
from .training import (
    TrainingModuleBaseSchema,
    TrainingModuleCreateSchema,
    TrainingModuleUpdateSchema,
    TrainingModuleResponseSchema,
    EmployeeTrainingBaseSchema,
    EmployeeTrainingCreateSchema,
    EmployeeTrainingUpdateSchema,
    EmployeeTrainingResponseSchema,
    EmployeeTrainingWithModuleSchema
)

__all__ = [
    # User schemas
    "UserBaseSchema",
    "UserCreateSchema", 
    "UserUpdateSchema",
    "UserResponseSchema",
    "UserLoginSchema",
    "UserLoginResponseSchema",
    
    # Task schemas
    "TaskBaseSchema",
    "TaskCreateSchema",
    "TaskUpdateSchema", 
    "TaskResponseSchema",
    "EmployeeTaskBaseSchema",
    "EmployeeTaskCreateSchema",
    "EmployeeTaskUpdateSchema",
    "EmployeeTaskResponseSchema",
    "EmployeeTaskWithDetailsSchema",
    
    # Document schemas
    "DocumentBaseSchema",
    "DocumentCreateSchema",
    "DocumentUpdateSchema",
    "DocumentResponseSchema", 
    "DocumentUploadResponseSchema",
    
    # Training schemas
    "TrainingModuleBaseSchema",
    "TrainingModuleCreateSchema",
    "TrainingModuleUpdateSchema",
    "TrainingModuleResponseSchema",
    "EmployeeTrainingBaseSchema", 
    "EmployeeTrainingCreateSchema",
    "EmployeeTrainingUpdateSchema",
    "EmployeeTrainingResponseSchema",
    "EmployeeTrainingWithModuleSchema"
]