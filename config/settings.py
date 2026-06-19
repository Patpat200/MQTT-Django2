"""
Django settings for config project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-zug-z3lju49kbkncu=((4gi*32d_glqlq63m60z!e@bdmpjwq&'

# DEBUG = True -> pratique pendant le développement (messages d'erreur détaillés),
# mais à mettre sur False si un jour le site est mis en ligne pour de vrai.
DEBUG = True

# NB : ['*'] et pas [*] -> ce sont des guillemets autour de l'étoile,
# sinon Python considère "*" comme du code et plante au démarrage.
ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'capteurs',
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

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,  # Django va chercher les templates dans capteurs/templates/
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Connexion à la base de données MySQL hébergée sur le PC Windows (VLAN Serveur)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'sae204',
        'USER': 'sae_user',
        'PASSWORD': 'Sae2024!',
        'HOST': '10.252.11.76',
        'PORT': '3306',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_TZ = False

USE_I18N = True

STATIC_URL = 'static/'
