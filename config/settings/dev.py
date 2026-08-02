from .base import *

# Development settings
DEBUG = True

# Disable security requirements for easier local debugging
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Disable axes brute-force lockout in development (re-enable in prod)
AXES_ENABLED = False
