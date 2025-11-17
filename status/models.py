from django.db import models
from django.utils import timezone
from django.conf import settings


class Service(models.Model):
    """Represents a service/component that we track status for"""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True, help_text="Show on status page")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_current_status(self):
        """Get the most recent status update for this service"""
        return self.status_updates.order_by('-created_at').first()

    def get_recent_updates(self, limit=5):
        """Get the most recent status updates"""
        return self.status_updates.order_by('-created_at')[:limit]


class StatusUpdate(models.Model):
    """Represents a status update for a service"""

    STATUS_CHOICES = [
        ('stable', 'Stable'),
        ('degraded', 'Degraded Performance'),
        ('partial', 'Partial Outage'),
        ('down', 'Major Outage'),
        ('maintenance', 'Maintenance'),
    ]

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='status_updates')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    problem = models.TextField(blank=True, help_text="Description of the problem (if any)")
    plan = models.TextField(blank=True, help_text="Plan to resolve the issue (if any)")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['service', '-created_at']),
        ]

    def __str__(self):
        return f"{self.service.name} - {self.get_status_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def get_status_color(self):
        """Return Tailwind color class for the status"""
        colors = {
            'stable': 'green',
            'degraded': 'yellow',
            'partial': 'orange',
            'down': 'red',
            'maintenance': 'blue',
        }
        return colors.get(self.status, 'gray')