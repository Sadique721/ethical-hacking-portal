import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# config/settings/base.py is 3 levels deep from root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Initialize environment variables reader
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, 'django-insecure-s&zn1go+$19c=(waf8dz24dcv9civhwk-)jy8qzq*!(i$id2k*'),
    ALLOWED_HOSTS=(list, ['*']),
)

# Load .env file if it exists at root
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
INSTALLED_APPS = [
    # Modern Admin Theme
    'jazzmin',
    
    # Django Default Apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-Party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'axes',
    
    # Custom Apps
    'MSA.apps.MsaConfig',
    'ctf.apps.CtfConfig',
    'utilities.apps.UtilitiesConfig',
    'writeups.apps.WriteupsConfig',
    'audit.apps.AuditConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # Django 6.0 Native Content Security Policy
    'django.middleware.csp.ContentSecurityPolicyMiddleware',
    
    # Axes Rate-Limiting Middleware for Authentication Lockouts
    'axes.middleware.AxesMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # CSP Context Processor to supply {{ csp_nonce }} to templates
                'django.template.context_processors.csp',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database config using dj-database-url (Defaults to SQLite for local dev)
DATABASES = {
    'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Caching Configuration
CACHES = {
    'default': env.cache('REDIS_URL', default='locmemcache://')
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication Backends (Add AxesBackend for lockout tracking)
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Axes Configuration
AXES_FAILURE_LIMIT = 5            # Number of login attempts before lockout
AXES_COOLOFF_TIME = 0.5           # Lockout duration in hours (30 minutes)
AXES_LOCKOUT_TEMPLATE = 'lockout.html'
AXES_RESET_ON_SUCCESS = True       # Reset failure counter on successful login

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static & Media files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication redirects
LOGIN_URL = '/login'
LOGIN_REDIRECT_URL = 'profile'
LOGOUT_REDIRECT_URL = 'login'

# Email backend configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

# Django 6.0 Background Tasks Configuration (Default to Immediate for Dev)
TASKS = {
    'default': {
        'BACKEND': 'django.tasks.backends.immediate.ImmediateBackend',
    }
}

# Django 6.0 Native Content Security Policy Configuration
from django.utils.csp import CSP
SECURE_CSP = {
    'default-src': [CSP.SELF],
    'script-src': [
        CSP.SELF,
        CSP.NONCE,
        'https://cdn.jsdelivr.net',
        'https://unpkg.com',
    ],
    'style-src': [
        CSP.SELF,
        'https://cdn.jsdelivr.net',
    ],
    'font-src': [
        CSP.SELF,
        'https://cdn.jsdelivr.net',
    ],
    'img-src': [
        CSP.SELF,
        'data:',
        'https://via.placeholder.com',
        'https://cdn.jsdelivr.net',
    ],
    'connect-src': [
        CSP.SELF,
    ],
    'object-src': [CSP.NONE],
}

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# OpenAPI Docs Setup
SPECTACULAR_SETTINGS = {
    'TITLE': 'Ethical Hacking Portal API',
    'DESCRIPTION': 'API endpoints for managing security researcher profiles, CTF challenges, CVE lookups, and audit trails.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# Jazzmin Admin Panel Customization
JAZZMIN_SETTINGS = {
    "site_title": "Hacker Admin",
    "site_header": "Hacker Admin",
    "site_brand": "Hacker Admin",
    "welcome_sign": "Welcome to Hacker Researcher Portal",
    "search_model": ["auth.User", "MSA.Profile"],
    "topmenu_links": [
        {"name": "Home", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Site Dashboard", "url": "/dashboard"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "MSA.Profile": "fas fa-id-card",
        "MSA.Contact": "fas fa-envelope",
        "ctf.Challenge": "fas fa-flag",
        "ctf.Submission": "fas fa-code-branch",
        "writeups.Post": "fas fa-terminal",
        "audit.AuditLog": "fas fa-shield-alt",
    },
    "order_with_respect_to": ["auth", "MSA", "ctf", "writeups", "audit"],
    "theme": "darkly",
}
JAZZMIN_UI_CHANGES = {
    "theme_css": "https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/darkly/bootstrap.min.css"
}
