from django.contrib import admin

from .models import AuditLog, Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = (
        'reference_no',
        'visitor_name',
        'visitor_phone',
        'host_name',
        'visit_date',
        'status',
        'checked_in_at',
        'checked_out_at',
    )
    list_filter = ('status', 'visit_date', 'created_at', 'checked_in_at', 'checked_out_at')
    search_fields = ('reference_no', 'qr_token', 'visitor_name', 'visitor_phone', 'host_name', 'host_email')
    readonly_fields = (
        'reference_no',
        'qr_token',
        'qr_code_image',
        'submitted_at',
        'checked_in_at',
        'checked_out_at',
        'checked_in_by',
        'checked_out_by',
        'created_at',
        'updated_at',
    )
    ordering = ('-created_at',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('visit', 'action', 'action_by', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('visit__reference_no', 'visit__visitor_name', 'action_by__username', 'note')
    readonly_fields = ('visit', 'action', 'action_by', 'note', 'created_at', 'updated_at')
    ordering = ('-created_at',)
