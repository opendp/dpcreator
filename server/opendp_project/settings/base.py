"""
Django settings for opendp_project project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""
import json
import os

from distutils.util import strtobool

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'SECRET_KEY!-ADD-REAL-KEY-HERE!--ADD-REAL-KEY!1234!')

# For field level encryption: https://django-cryptography.readthedocs.io/en/latest/settings.html
CRYPTOGRAPHY_KEY = os.getenv('CRYPTOGRAPHY_KEY', 'CRYPTOGRAPHY_KEY!-ADD-REAL-KEY!1234!')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

INSTALLED_APPS = [
    'channels', # Django channels..
    'opendp_apps.async_messages',
    #
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'django.contrib.sites',
    #
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'polymorphic',
    'opendp_apps.model_helpers',
    'opendp_apps.content_pages',
    'opendp_apps.dataverses',
    'opendp_apps.user',
    'opendp_apps.dataset',
    'opendp_apps.analysis',
    'opendp_apps.terms_of_access',
    'opendp_apps.banner_messages',
    'opendp_apps.communication',
    'opendp_apps.profiler',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'opendp_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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


# -----------------------------------------------
# REDIS settings
# -----------------------------------------------
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = os.environ.get('REDIS_PORT', 6379)
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', '')

# reference: https://docs.celeryproject.org/en/stable/getting-started/brokers/redis.html
if REDIS_PASSWORD:
    REDIS_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
else:
    REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'


# -----------------------------------------------
# ASGI, Channels settings
# -----------------------------------------------
#WSGI_APPLICATION = 'opendp_project.wsgi.application'

ASGI_APPLICATION = "opendp_project.asgi.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [REDIS_URL],
        },
    },
}

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'NAME': os.getenv('DB_NAME', 'postgres'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'PORT': int(os.getenv('DB_PORT', 5432)),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TIME_ZONE', 'UTC')

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = os.environ.get('STATIC_URL', '/static/')
STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static', 'dist'))

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

USE_DEV_STATIC_SERVER = strtobool(os.environ.get('USE_DEV_STATIC_SERVER', 'True'))

# global settings for the REST framework
REST_FRAMEWORK = {
    # 'EXCEPTION_HANDLER': 'opendp_apps.utils.view_helper.opendp_exception_handler',
    'DEFAULT_PERMISSION_CLASSES': [
        # 'rest_framework.permissions.IsAdminUser',
        # 'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination', 'PAGE_SIZE': 10
}


# -----------------------------------
# Handling uploaded files
# -----------------------------------

# (1) If using nginx, should be the same value as NGINX_MAX_UPLOAD_SIZE
# ref: https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-DATA_UPLOAD_MAX_MEMORY_SIZE
# 20971520 bytes = 20 MB
#
DATA_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('DATA_UPLOAD_MAX_MEMORY_SIZE', '20971520'))

# (2) If file exceed this size, it will be streamed to a "temp" location
# ref: https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-FILE_UPLOAD_MAX_MEMORY_SIZE
#  2621440 byes = 2.5 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = int(os.environ.get('FILE_UPLOAD_MAX_MEMORY_SIZE', '2621440'))
# (2a) Where the file is streamed too -- needs to be secure!
FILE_UPLOAD_TEMP_DIR = os.environ.get('FILE_UPLOAD_TEMP_DIR', '/tmp')

# (3) Storage root for uploaded files
#   - will be objects on cloud service. e.g. S3, Azure, etc.
#
UPLOADED_FILE_STORAGE_ROOT = os.getenv('UPLOADED_FILE_STORAGE_ROOT',
                                       os.path.join(BASE_DIR, 'test_setup', 'private_uploaded_data'))
if not os.path.isdir(UPLOADED_FILE_STORAGE_ROOT):
    os.makedirs(UPLOADED_FILE_STORAGE_ROOT)

RELEASE_FILE_STORAGE_ROOT = os.getenv('RELEASE_FILE_STORAGE_ROOT',
                                      os.path.join(BASE_DIR, 'test_setup', 'public_release_files'))
if not os.path.isdir(RELEASE_FILE_STORAGE_ROOT):
    os.makedirs(RELEASE_FILE_STORAGE_ROOT)

# -------------------------------------
AUTHENTICATION_BACKENDS = (
 'django.contrib.auth.backends.ModelBackend',
 'allauth.account.auth_backends.AuthenticationBackend',
 )

SITE_ID = 3

LOGIN_REDIRECT_URL = '/ui'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        }
    }
}

AUTH_USER_MODEL = 'user.OpenDPUser'
REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'opendp_apps.user.serializers.CustomRegisterSerializer',
}
REST_AUTH_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'opendp_apps.user.serializers.CustomLoginSerializer',
    'USER_DETAILS_SERIALIZER': 'opendp_apps.user.serializers.OpenDPUserSerializer',
}
# ALLOWED_HOSTS=['*']

DEFAULT_ALLOWED_HOSTS = '0.0.0.0,127.0.0.1,localhost,server'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', DEFAULT_ALLOWED_HOSTS).split(',')

CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOWED_ORIGINS = (
    # 'http://localhost:8000',
    # 'http://127.0.0.1:8000',
    #'http://0.0.0.0:8000',
    # 8080
    'http://127.0.0.1:8080',
)


SENDGRID_SANDBOX_MODE_IN_DEBUG = False
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.sendgrid.net')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'apikey')
EMAIL_HOST_PASSWORD = os.environ.get('SENDGRID_API_KEY', 'sendgrid-key-not-set')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

# TODO: Make this a product-wide address.
# To verify a new account:
#   1. Go to https://app.sendgrid.com/settings/sender_auth/senders
#   2. Click "verify new sender" and proceed
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'info@opendp.org')

# Possible settings for ACCOUNT_EMAIL_VERIFICATION: 'none' or 'mandatory';
#   - 'mandatory' requires working settings for EMAIL_HOST, EMAIL_USER, etc.
#
ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'none')  # 'mandatory'
ACCOUNT_EMAIL_REQUIRED = 'true'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = '/log-in/'
ACCOUNT_TEMPLATE_EXTENSION = 'html'

# This setting is necessary to enable checking of the old password when changing the password
OLD_PASSWORD_FIELD_ENABLED = 'true'

# ---------------------------
# Profiler - Dataset reading
#   - default parameters
# ---------------------------
PROFILER_COLUMN_LIMIT = int(os.environ.get('PROFILER_COLUMN_LIMIT', 20))
assert PROFILER_COLUMN_LIMIT >= 1, 'PROFILER_COLUMN_LIMIT must be at least 1'

# -----------------------------------------------
# Websocket prefix.
# When using https, set it to 'wss://'
# -----------------------------------------------
WEBSOCKET_PREFIX = os.environ.get('WEBSOCKET_PREFIX', 'ws://')
assert WEBSOCKET_PREFIX in ('ws://', 'wss://'), \
    "Django settings error: 'WEBSOCKET_PREFIX' must be set to 'ws://' or 'wss://'"

# ---------------------------
# Celery Configuration Options
# ---------------------------
#CELERY_TIMEZONE = os.environ.get('America/New_York', 'CELERY_TIMEZONE')
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# ------------------------------------------------------
# Application name for deposit use
# ------------------------------------------------------
DP_CREATOR_APP_NAME = os.environ.get('DP_CREATOR_APP_NAME', 'DP Creator (test)')

# ---------------------------
# Cookies
# ---------------------------
SESSION_EXPIRE_AT_BROWSER_CLOSE = bool(strtobool(os.environ.get('SESSION_EXPIRE_AT_BROWSER_CLOSE', 'True')))
SESSION_DEFAULT_COOKIE_AGE = (60 * 60) * 2  # 2 hour sessions, in seconds
SESSION_COOKIE_AGE = int(os.getenv('SESSION_COOKIE_AGE', SESSION_DEFAULT_COOKIE_AGE))


# SESSION_COOKIE_NAME = os.environ.get('SESSION_COOKIE_NAME', 'dpcreator')
# CSRF_COOKIE_NAME = os.environ.get('CSRF_COOKIE_NAME', 'dpcreator_csrf')
# discard a process after executing task, because automl solvers are incredibly leaky
# CELERY_WORKER_MAX_TASKS_PER_CHILD = 1

# Uncomment this out to see raw SQL in logs
# LOGGING = {
#     'version': 1,
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#         }
#     },
#     'loggers': {
#         'django.db.backends': {
#             'level': 'DEBUG',
#             'handlers': ['console'],
#         }
#     }
# }
