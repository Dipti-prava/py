"""
Django settings for myproject project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os

import datetime
from dotenv import load_dotenv

from .config.crypt import decrypt

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file
load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
SECRET_KEY = decrypt('gAAAAABl1ZCZnkKRKhPSvUTcp0w2lr3HwSmX3xduXMD6ItXyQWeF4Ajx7kRBbplyYopn7hjaQruJwyaNEyf8pfNA28TD29EVXGDY9zOcJUOLBGFrxPzDF4c6eG1bTlSCz4HzVc982RtYOQp0f3-dwv6fVu7gHCrcwa5XYcs8WGDavIXJWFsvbV0=')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'rest_framework_simplejwt',
    'corsheaders',
    'myapp'
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}


def get_custom_primary_key_settings():
    custom_id_fields = {
        'User': 'user_id',
        'Profile': 'profile_id',
        # Add more models and their respective custom primary key fields here
    }
    # You might dynamically fetch models and their custom primary keys here

    jwt_settings = {}
    for model, custom_id_field in custom_id_fields.items():
        jwt_settings[f'{model.upper()}_ID_FIELD'] = custom_id_field

    return jwt_settings


SIMPLE_JWT = {
    'TOKEN_OBTAIN_PAIR_SERIALIZER': 'myproject.myapp.serializers.CustomTokenObtainPairSerializer',
    'AUTH_HEADER_TYPES': ('Bearer',),
    # 'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=525960),
    # "ACCESS_TOKEN_LIFETIME": datetime.timedelta(minutes=30),
    # "REFRESH_TOKEN_LIFETIME": datetime.timedelta(days=1),
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=1),  # Set access token lifetime to 10 minutes
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    **get_custom_primary_key_settings(),
}

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'myapp.middleware.UpdateLastActivityMiddleware',
]
ROOT_URLCONF = 'myproject.urls'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# SESSION_COOKIE_SAMESITE = 'Strict'
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

WSGI_APPLICATION = 'myproject.wsgi.application'

AUTH_USER_MODEL = 'myapp.User'

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

SESSION_COOKIE_SECURE = True
CORS_ALLOW_HEADERS = [
    'Content-Type',
    'x-captcha-key',
    'x-session-key',
    'Authorization',
    'Set-Cookie'
]
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = [
#     'http://192.168.0.117:3001',
#     # Add more origins as needed
# ]
CORS_ALLOW_CREDENTIALS = True

CORS_ORIGIN_WHITELIST = [
    'http://192.168.0.117:3001',  # Whitelist your Angular app's domain
    # Add other allowed origins as needed
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {lineno} {message}',  # Include {message}
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
