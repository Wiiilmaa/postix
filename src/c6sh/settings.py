import os

from django.contrib import messages
from django.utils.crypto import get_random_string

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if os.getenv('C6SH_SECRET', ''):
    SECRET_KEY = os.getenv('C6SH_SECRET', '')
else:
    SECRET_FILE = os.path.join(BASE_DIR, '.secret')
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, 'r') as f:
            SECRET_KEY = f.read().strip()
    else:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        SECRET_KEY = get_random_string(50, chars)
        with open(SECRET_FILE, 'w') as f:
            os.chmod(SECRET_FILE, 0o600)
            os.chown(SECRET_FILE, os.getuid(), os.getgid())
            f.write(SECRET_KEY)

DEBUG = os.getenv('C6SH_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'rest_framework',
    'solo',
    'c6sh.core',
    'c6sh.desk',
    'c6sh.api',
    'c6sh.backoffice',
    'c6sh.troubleshooter',
)


try:
    import django_extensions  # noqa
    INSTALLED_APPS += ('django_extensions', )
except ImportError:
    pass


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'c6sh.urls'
WSGI_APPLICATION = 'c6sh.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + os.getenv('C6SH_DB_TYPE', 'sqlite3'),
        'NAME': os.getenv('C6SH_DB_NAME', 'db.sqlite3'),
        'USER': os.getenv('C6SH_DB_USER', ''),
        'PASSWORD': os.getenv('C6SH_DB_PASS', ''),
        'HOST': os.getenv('C6SH_DB_HOST', ''),
        'PORT': os.getenv('C6SH_DB_PORT', ''),
        'CONN_MAX_AGE': 300 if os.getenv('C6SH_DB_TYPE', 'sqlite3') != 'sqlite3' else 0,
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'c6sh.troubleshooter.context.processor'
            ],
        }
    }
]

LANGUAGE_CODE = 'de'
LANGUAGES = (
    ('en', 'English'),
    ('de', 'German'),
)
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locale')
]

STATIC_URL = os.getenv('C6SH_STATIC_URL', '/static/c6sh/')
STATIC_ROOT = os.getenv('C6SH_STATIC_ROOT', '/srv/static/c6sh/')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'c6sh', 'static'),
]
MEDIA_ROOT = os.path.join(BASE_DIR, 'c6sh', 'media')

AUTH_USER_MODEL = 'core.User'

MESSAGE_TAGS = {
    messages.INFO: 'info',
    messages.ERROR: 'danger',
    messages.WARNING: 'warning',
    50: 'critical',
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'c6sh.api.auth.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',),
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
