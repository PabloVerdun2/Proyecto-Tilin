from pathlib import Path
import os
from decouple import config, Csv


BASE_DIR = Path(__file__).resolve().parent.parent

# Secretos y entorno: se leen del .env (ver .env.example).
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)          # produccion: False
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

# Aplicaciones instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cuentas',  # Tu app personalizada
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Enrutador principal
ROOT_URLCONF = 'mi_proyecto.urls'

# Configuración de templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'cuentas', 'templates')],
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

# WSGI
WSGI_APPLICATION = 'mi_proyecto.wsgi.application'

# Base de datos: valores por entorno (ver .env.example).
# Local: SQL Server + autenticacion de Windows (trusted_connection).
# Produccion: definir DB_USER/DB_PASSWORD y DB_TRUSTED_CONNECTION=no.
_db_options = {'driver': config('DB_DRIVER', default='ODBC Driver 17 for SQL Server')}
if config('DB_TRUSTED_CONNECTION', default='yes').lower() == 'yes':
    _db_options['trusted_connection'] = 'yes'

DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='mssql'),
        'NAME': config('DB_NAME', default='GourmetDB'),
        'HOST': config('DB_HOST', default='localhost\\SQLEXPRESS'),
        'PORT': config('DB_PORT', default=''),
        'USER': config('DB_USER', default=''),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'OPTIONS': _db_options,
    }
}

# Validadores de contraseña
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

# Configuración regional
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Asuncion'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'cuentas', 'static')]

# Campo automático por defecto
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# URL para login (si usás @login_required)
LOGIN_URL = '/login/'

AUTH_USER_MODEL = 'cuentas.CustomUser'
AUTHENTICATION_BACKENDS = ['cuentas.backend.EmailBackend']
