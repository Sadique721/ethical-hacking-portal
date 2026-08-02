from .base import *

# Development settings
DEBUG = True

# Disable security requirements for easier local debugging
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
