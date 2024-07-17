import json
import os
from unipath import Path

from .base import *

DEV_SECRETS_PATH = SETTINGS_PATH.child("dev_secrets.json")
with open(os.path.join(DEV_SECRETS_PATH)) as f: secrets = json.loads(f.read())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'analytics_automated_db',
        'USER': get_secret("USER", secrets),
        'PASSWORD': get_secret("PASSWORD", secrets),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CORS_ALLOW_HEADERS = (
    'x-csrf-token',
    'content-type',
)
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CORS_ORIGIN_WHITELIST = (
        'http://127.0.0.1:3000',   
        'http://127.0.0.1:4000',
        'http://127.0.0.1:8000',
        'https://127.0.0.1:3000',   
        'https://127.0.0.1:4000',
        'https://127.0.0.1:8000',
        'http://localhost:3000',
        'http://localhost:4000',
        'http://localhost:8000',
        'https://localhost:3000',
        'https://localhost:4000',
        'https://localhost:8000',
        'http://localhost:80',
        'https://localhost:80',
        'http://localhost',
        'https://localhost',
        'http://127.0.0.1:80',
        'https://127.0.0.1:80',
        'http://127.0.0.1',
        'https://127.0.0.1',
)

CSRF_TRUSTED_ORIGINS = (
        'http://127.0.0.1:3000',   
        'http://127.0.0.1:4000',
        'http://127.0.0.1:8000',
        'https://127.0.0.1:3000',   
        'https://127.0.0.1:4000',
        'https://127.0.0.1:8000',
        'http://localhost:3000',
        'http://localhost:4000',
        'http://localhost:8000',
        'https://localhost:3000',
        'https://localhost:4000',
        'https://localhost:8000',
        'http://localhost:80',
        'https://localhost:80',
        'http://localhost',
        'https://localhost',
        'http://127.0.0.1:80',
        'https://127.0.0.1:80',
        'http://127.0.0.1',
        'https://127.0.0.1',
)
SECRET_KEY = get_secret("SECRET_KEY", secrets)

DEBUG = True

INSTALLED_APPS = (
    'bootstrap_admin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'analytics_automated',
    'rest_framework',
    'corsheaders',
    'smuggler',
    'debug_toolbar',
)

DEBUG_TOOLBAR_CONFIG = {
    'JQUERY_URL': "/static/js/jquery.min.js",
}
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# TODO: Change this for staging and production
MEDIA_URL = '/submissions/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'submissions/')
STATIC_URL = '/static/'
# Change the test runner
#TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

ADMIN_EMAIL = "daniel.buchan@ucl.ac.uk"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.cs.ucl.ac.uk'
EMAIL_PORT = '25'
# EMAIL_HOST_USER = 'psipred@cs.ucl.ac.uk'
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'psipred@cs.ucl.ac.uk'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10240

