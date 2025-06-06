import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'secret')
ALGORITHM = "HS256"

DEBUG = os.getenv('DEBUG', False) == 'True'

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "https://localhost:8000",
]


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'movies',
    'users',
    'notify',
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

ROOT_URLCONF = 'admin_service.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'admin_service.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('PG_NAME', 'name'),
        'USER': os.getenv('PG_USER', 'user'),
        'PASSWORD': os.getenv('PG_PASSWORD', 'password'),
        'HOST': os.getenv('PG_HOST', '127.0.0.1'),
        'PORT': os.getenv('PG_PORT', 5432),
        'OPTIONS': {
            'options': '-c search_path=public,admin,content,notify',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_SERVICE_HOST = os.getenv('AUTH_SERVICE_HOST', '127.0.0.1')
AUTH_SERVICE_PORT = os.getenv('AUTH_SERVICE_PORT', '8000')
AUTH_API_LOGIN_URL = (
    f"http://{AUTH_SERVICE_HOST}:{AUTH_SERVICE_PORT}/api/v1/auth/users/login"
)
AUTH_USER_MODEL = "users.AdminUser"
AUTHENTICATION_BACKENDS = [
    'users.backends.AdminBackend',
]

NOTIFY_API_SERVICE_HOST = os.getenv('NOTIFY_API_SERVICE_HOST', '127.0.0.1')
NOTIFY_API_SERVICE_PORT = os.getenv('NOTIFY_API_SERVICE_PORT', '8000')
NOTIFY_API_URL = (
    f"http://{NOTIFY_API_SERVICE_HOST}:{NOTIFY_API_SERVICE_PORT}.internal/api"
    f"/v1/messages/"
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
