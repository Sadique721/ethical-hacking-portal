from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'ip_address', 'details')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'action', 'details', 'ip_address')
    
    # Audit logs should be read-only in the admin panel to guarantee integrity
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
