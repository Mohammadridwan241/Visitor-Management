import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def env_bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    return [item.strip() for item in os.getenv(name, default).split(',') if item.strip()]


def hostname_from_url(url):
    if not url:
        return ''
    parsed = urlparse(url)
    return (parsed.hostname or '').strip()


def merge_unique(items):
    merged = []
    for item in items:
        value = (item or '').strip()
        if value and value not in merged:
            merged.append(value)
    return merged


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-local-dev-change-me')
DEBUG = env_bool('DJANGO_DEBUG', True)
SITE_URL = os.getenv('SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME', '').strip()

ALLOWED_HOSTS = merge_unique(
    env_list('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost')
    + [hostname_from_url(SITE_URL), RENDER_EXTERNAL_HOSTNAME]
)

CSRF_TRUSTED_ORIGINS = merge_unique(
    env_list('DJANGO_CSRF_TRUSTED_ORIGINS')
    + ([SITE_URL] if SITE_URL else [])
    + ([f'https://{RENDER_EXTERNAL_HOSTNAME}'] if RENDER_EXTERNAL_HOSTNAME else [])
)

INSTALLED_APPS = [
    'apps.accounts',
    'apps.common',
    'apps.visitors',
    'apps.reception',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
AUTH_USER_MODEL = 'accounts.User'

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
            ],
        },
    },
]


def database_from_url(url):
    if not url or url.startswith('sqlite:///'):
        name = url.replace('sqlite:///', '', 1) if url else 'db.sqlite3'
        return {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / name}
    parsed = urlparse(url)
    engine = 'django.db.backends.postgresql'
    if parsed.scheme.startswith('mysql'):
        engine = 'django.db.backends.mysql'
    return {
        'ENGINE': engine,
        'NAME': parsed.path.lstrip('/'),
        'USER': parsed.username or '',
        'PASSWORD': parsed.password or '',
        'HOST': parsed.hostname or '',
        'PORT': parsed.port or '',
    }


DATABASES = {
    'default': database_from_url(os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = os.getenv('DJANGO_TIME_ZONE', 'Asia/Dhaka')
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'reception:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Visitor Management System API',
    'DESCRIPTION': 'Receptionist workflow APIs for visitor registration, QR lookup, check-in, and checkout.',
    'VERSION': '1.0.0',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['console'], 'level': 'INFO'},
}
