# core/settings.py

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv # Importa a biblioteca

# Carrega as variáveis do arquivo .env para o ambiente
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- LEITURA DAS VARIÁVEIS DE AMBIENTE ---
# As chaves agora são lidas de forma segura do arquivo .env ou do ambiente de produção.
SECRET_KEY = os.getenv("SECRET_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# O valor de DEBUG é convertido de string "True" para o booleano True.
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Application definition
INSTALLED_APPS = [
    "filmes",
    "usuarios",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "filmes" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "filmes.context_processors.custom_genres_processor",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# --- CONFIGURAÇÃO DA BASE DE DADOS ---
# Configuração padrão para o desenvolvimento local com SQLite.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# --- CONFIGURAÇÃO DE ARQUIVOS ESTÁTICOS ---
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]


# --- CONFIGURAÇÃO DE ARQUIVOS DE MÍDIA (UPLOADS) ---
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "mediafiles"


# --- CONFIGURAÇÕES DE LOGIN/LOGOUT ---
LOGIN_URL = "usuarios:login" 
LOGOUT_REDIRECT_URL = "home"
LOGIN_REDIRECT_URL = "home"


# --- CONFIGURAÇÕES DE EMAIL ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')