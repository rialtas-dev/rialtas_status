"""
API schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from ninja import Schema


# Request Schemas
class StatusUpdateCreateSchema(Schema):
    """Schema for creating a new status update"""
    service_id: int
    status: str  # One of: stable, degraded, partial, down, maintenance
    comments: Optional[str] = ""
    plan: Optional[str] = ""


# Response Schemas
class ServiceSchema(Schema):
    """Schema for service information"""
    id: int
    name: str
    description: str
    order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StatusUpdateSchema(Schema):
    """Schema for status update information"""
    id: int
    service_id: int
    service_name: str
    status: str
    status_display: str
    comments: str
    plan: str
    created_at: datetime
    created_by_username: Optional[str] = None


class ServiceWithStatusSchema(Schema):
    """Schema for service with current status"""
    id: int
    name: str
    description: str
    order: int
    is_active: bool
    current_status: Optional[StatusUpdateSchema] = None


class MessageSchema(Schema):
    """Generic message response schema"""
    message: str


class ErrorSchema(Schema):
    """Error response schema"""
    error: str
    details: Optional[str] = None
