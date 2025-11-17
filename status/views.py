from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Service, StatusUpdate


def status_page(request):
    """Main status page showing all services and their current status"""
    services = Service.objects.filter(is_active=True).prefetch_related('status_updates__created_by')

    services_data = []
    overall_status = 'stable'

    for service in services:
        current_status = service.get_current_status()
        recent_updates = service.get_recent_updates(limit=5)

        services_data.append({
            'service': service,
            'current_status': current_status,
            'recent_updates': recent_updates,
        })

        # Determine overall status (worst case wins)
        if current_status:
            if current_status.status == 'down':
                overall_status = 'down'
            elif current_status.status == 'partial' and overall_status != 'down':
                overall_status = 'partial'
            elif current_status.status == 'degraded' and overall_status not in ['down', 'partial']:
                overall_status = 'degraded'
            elif current_status.status == 'maintenance' and overall_status == 'stable':
                overall_status = 'maintenance'

    context = {
        'services_data': services_data,
        'overall_status': overall_status,
    }

    return render(request, 'status/status_page.html', context)


def service_detail(request, service_id):
    """Detail page for a specific service showing recent updates"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    recent_updates = service.get_recent_updates(limit=5)

    context = {
        'service': service,
        'recent_updates': recent_updates,
    }

    return render(request, 'status/service_detail.html', context)


def service_history_json(request, service_id):
    """API endpoint to get service history as JSON"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    updates = service.status_updates.all()[:10]

    data = {
        'service': service.name,
        'updates': [
            {
                'status': update.get_status_display(),
                'status_code': update.status,
                'problem': update.problem,
                'plan': update.plan,
                'created_at': update.created_at.isoformat(),
                'created_by': update.created_by.username if update.created_by else None,
            }
            for update in updates
        ]
    }

    return JsonResponse(data)