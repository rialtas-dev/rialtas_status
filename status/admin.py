from django.contrib import admin
from django.utils.html import format_html
from .models import Service, StatusUpdate


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'current_status_badge', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['order', 'name']
    list_editable = ['order', 'is_active']

    def current_status_badge(self, obj):
        status_update = obj.get_current_status()
        if status_update:
            color_map = {
                'stable': '#10b981',
                'degraded': '#f59e0b',
                'partial': '#f97316',
                'down': '#ef4444',
                'maintenance': '#3b82f6',
            }
            color = color_map.get(status_update.status, '#6b7280')
            return format_html(
                '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 4px; font-size: 12px;">{}</span>',
                color,
                status_update.get_status_display()
            )
        return format_html('<span style="color: #9ca3af;">No status</span>')

    current_status_badge.short_description = 'Current Status'


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['service', 'status_badge', 'created_at', 'created_by_display', 'has_comments', 'has_plan']
    list_filter = ['status', 'service', 'created_at', 'created_by']
    search_fields = ['service__name', 'comments', 'plan', 'created_by__username', 'created_by__first_name', 'created_by__last_name']
    readonly_fields = ['created_at', 'created_by_display']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Status Information', {
            'fields': ('service', 'status', 'created_at', 'created_by_display')
        }),
        ('Details', {
            'fields': ('comments', 'plan'),
            'description': 'Provide comments about this status update and any plan to resolve issues.'
        }),
    )

    def status_badge(self, obj):
        color_map = {
            'stable': '#10b981',
            'degraded': '#f59e0b',
            'partial': '#f97316',
            'down': '#ef4444',
            'maintenance': '#3b82f6',
        }
        color = color_map.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 4px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'Status'

    def has_comments(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            '#10b981' if obj.comments else '#9ca3af',
            '✓' if obj.comments else '—'
        )

    has_comments.short_description = 'Comments'

    def has_plan(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            '#10b981' if obj.plan else '#9ca3af',
            '✓' if obj.plan else '—'
        )

    has_plan.short_description = 'Plan'

    def created_by_display(self, obj):
        if obj.created_by:
            full_name = obj.created_by.get_full_name()
            if full_name:
                return full_name
            return obj.created_by.username
        return '—'

    created_by_display.short_description = 'Created By'

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)