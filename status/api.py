"""
Django Ninja API endpoints for status updates
"""
from typing import List

from django.shortcuts import get_object_or_404
from ninja import NinjaAPI
from ninja.errors import HttpError

from .api_auth import APIKeyAuth
from .api_schemas import (
    StatusUpdateCreateSchema,
    StatusUpdateSchema,
    ServiceWithStatusSchema,
    MessageSchema,
    ErrorSchema,
)
from .models import Service, StatusUpdate


# Helper functions to convert models to dictionaries
def status_update_to_dict(update):
    """Convert a StatusUpdate instance to a dictionary"""
    return {
        'id': update.id,
        'service_id': update.service.id,
        'service_name': update.service.name,
        'status': update.status,
        'status_display': update.get_status_display(),
        'comments': update.comments,
        'plan': update.plan,
        'created_at': update.created_at,
        'created_by_username': update.created_by.username if update.created_by else None,
    }


def service_to_dict(service, include_status=True):
    """Convert a Service instance to a dictionary"""
    result = {
        'id': service.id,
        'name': service.name,
        'description': service.description,
        'order': service.order,
        'is_active': service.is_active,
    }

    if include_status:
        current_status = service.get_current_status()
        result['current_status'] = status_update_to_dict(current_status) if current_status else None

    return result


# Create API instance with authentication
api = NinjaAPI(
    title="Rialtas Status API",
    version="1.0.0",
    description="API for managing service status updates",
    auth=APIKeyAuth(),
)


# Status Update Endpoints
@api.post(
    "/status-updates",
    response={201: StatusUpdateSchema, 400: ErrorSchema},
    summary="Create a new status update",
    description="Create a new status update for a service. Requires valid API key.",
)
def create_status_update(request, payload: StatusUpdateCreateSchema):
    """
    Create a new status update for a service.

    **Required fields:**
    - service_id: ID of the service to update
    - status: One of: stable, degraded, partial, down, maintenance

    **Optional fields:**
    - comments: Additional comments about the status
    - plan: Plan to resolve any issues
    """
    # Validate service exists
    service = get_object_or_404(Service, id=payload.service_id)

    # Validate status choice
    valid_statuses = [choice[0] for choice in StatusUpdate.STATUS_CHOICES]
    if payload.status not in valid_statuses:
        raise HttpError(
            400,
            f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    # Create status update
    status_update = StatusUpdate.objects.create(
        service=service,
        status=payload.status,
        comments=payload.comments or "",
        plan=payload.plan or "",
        created_by=None,  # API updates don't have a user
    )

    return 201, status_update_to_dict(status_update)


@api.get(
    "/status-updates",
    response=List[StatusUpdateSchema],
    summary="List all status updates",
    description="Get a list of all status updates, ordered by most recent first.",
)
def list_status_updates(request, limit: int = 50):
    """
    List status updates with optional limit.

    **Query parameters:**
    - limit: Maximum number of results (default: 50, max: 200)
    """
    if limit > 200:
        limit = 200

    updates = StatusUpdate.objects.select_related('service', 'created_by').all()[:limit]
    return [status_update_to_dict(update) for update in updates]


@api.get(
    "/status-updates/{update_id}",
    response={200: StatusUpdateSchema, 404: ErrorSchema},
    summary="Get a specific status update",
    description="Retrieve details of a specific status update by ID.",
)
def get_status_update(request, update_id: int):
    """
    Get a specific status update by ID.
    """
    update = get_object_or_404(StatusUpdate.objects.select_related('service', 'created_by'), id=update_id)
    return status_update_to_dict(update)


# Service Endpoints
@api.get(
    "/services",
    response=List[ServiceWithStatusSchema],
    summary="List all services",
    description="Get a list of all services with their current status.",
)
def list_services(request, active_only: bool = True):
    """
    List all services with their current status.

    **Query parameters:**
    - active_only: Only return active services (default: true)
    """
    services = Service.objects.all()
    if active_only:
        services = services.filter(is_active=True)

    return [service_to_dict(service) for service in services]


@api.get(
    "/services/{service_id}",
    response={200: ServiceWithStatusSchema, 404: ErrorSchema},
    summary="Get a specific service",
    description="Retrieve details of a specific service with its current status.",
)
def get_service(request, service_id: int):
    """
    Get a specific service by ID with its current status.
    """
    service = get_object_or_404(Service, id=service_id)
    return service_to_dict(service)


@api.get(
    "/services/{service_id}/history",
    response=List[StatusUpdateSchema],
    summary="Get service status history",
    description="Get the status update history for a specific service.",
)
def get_service_history(request, service_id: int, limit: int = 20):
    """
    Get the status history for a specific service.

    **Query parameters:**
    - limit: Maximum number of results (default: 20, max: 100)
    """
    service = get_object_or_404(Service, id=service_id)

    if limit > 100:
        limit = 100

    updates = service.status_updates.select_related('created_by').all()[:limit]
    return [status_update_to_dict(update) for update in updates]


# Health check endpoint (no authentication required)
@api.get(
    "/health",
    response=MessageSchema,
    auth=None,  # No authentication required
    summary="API health check",
    description="Check if the API is running. No authentication required.",
)
def health_check(request):
    """
    Health check endpoint - no authentication required.
    """
    return {"message": "API is running"}
