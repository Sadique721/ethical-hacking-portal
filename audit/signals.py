from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from .models import AuditLog

def get_client_ip(request):
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action="LOGIN_SUCCESS",
        ip_address=get_client_ip(request),
        details=f"User {user.username} logged in successfully."
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        AuditLog.objects.create(
            user=user,
            action="LOGOUT",
            ip_address=get_client_ip(request),
            details=f"User {user.username} logged out."
        )

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username', 'Unknown')
    AuditLog.objects.create(
        user=None,
        action="LOGIN_FAILED",
        ip_address=get_client_ip(request) if request else None,
        details=f"Failed login attempt for username: {username}"
    )
