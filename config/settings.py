import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'unsafe-development-key')
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'
ALLOWED_HOSTS = [host.strip() for host in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

INSTALLED_APPS = [
    'django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes',
    'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles',
    'inertia', 'django_vite', 'core', 'business',
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
    'core.middleware.JsonRequestMiddleware',
    'inertia.middleware.InertiaMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True,
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {
    'ENGINE': 'django.db.backends.postgresql', 'NAME': os.getenv('POSTGRES_DB', 'btp_manager'),
    'USER': os.getenv('POSTGRES_USER', 'btp_user'), 'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'btp_password'),
    'HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'), 'PORT': os.getenv('POSTGRES_PORT', '5432'),
}}
if os.getenv('DATABASE_URL'):
    ssl_require = not DEBUG
    if os.getenv('DISABLE_DATABASE_SSL', 'False').lower() == 'true':
        ssl_require = False
    DATABASES['default'] = dj_database_url.parse(os.environ['DATABASE_URL'], conn_max_age=600, ssl_require=ssl_require)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Abidjan'
USE_I18N = True
USE_TZ = True
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = 'login'
INERTIA_LAYOUT = 'base.html'
DJANGO_VITE = {'default': {'dev_mode': DEBUG, 'dev_server_host': 'localhost', 'dev_server_port': 5173}}
DJANGO_VITE_ASSETS_PATH = BASE_DIR / 'frontend' / 'dist'
# Inclure frontend/dist dans STATICFILES_DIRS uniquement s'il existe (évite
# une erreur de démarrage si le build frontend n'a pas encore été exécuté).
STATICFILES_DIRS = [DJANGO_VITE_ASSETS_PATH] if DJANGO_VITE_ASSETS_PATH.exists() else []

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
