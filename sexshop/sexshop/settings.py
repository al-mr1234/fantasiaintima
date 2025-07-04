from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SECRET_KEY = 'django-insecure-g=^shdgaccc+=*k9*^)mz@e)tzdq5^wnj7q3-in%7-)(pn+4c%'

DEBUG = True

ALLOWED_HOSTS = []

# Aplicaciones instaladas
INSTALLED_APPS = [
    'sexshop',
    'appsexshop.apps.AppsexshopConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'social_django',  # Nuevo: social-auth-app-django
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

ROOT_URLCONF = 'sexshop.urls'



# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            'sexshop/templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                # Nuevos para social-auth
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'sexshop.wsgi.application'

# Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'fantasiaintima2',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
        'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
    }
}

# Validación de contraseñas
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

# Internacionalización
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Archivos estáticos
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    'appsexshop/static',
]

# Archivos multimedia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Sesiones
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Usa la base de datos para almacenar sesiones
SESSION_COOKIE_HTTPONLY = True                         # Evita que JavaScript acceda a las cookies de sesión (más seguro)
SESSION_COOKIE_SECURE = False                          # Está bien para desarrollo (usa True en producción con HTTPS)
SESSION_COOKIE_AGE = 1209600                           # Opcional: duración de la sesión (en segundos, aquí son 2 semanas)
SESSION_SAVE_EVERY_REQUEST = True    

# Login/logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Autenticación con Google (social-auth)
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Reemplaza con tus claves reales de Google OAuth
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = ''
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = ''   

# Clave por defecto para modelos
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',

    'social_core.pipeline.user.create_user',

    'appsexshop.pipeline.create_user_in_custom_table',  # Crea en tu tabla personalizada

    'social_core.pipeline.social_auth.associate_user',  # 🔄 Aquí debe ir antes de guardar sesión
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',

    'appsexshop.pipeline.save_custom_session',  # ✅ Esto debe ir al final, cuando ya hay user asociado
)

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587 #es el que utiliza el protocolo smtp
EMAIL_HOST_USER = 'store.fantasia.intima@gmail.com'
EMAIL_HOST_PASSWORD = 'mrdz aema ouvd tcts'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


