"""
Django settings for rms project.

Generated by 'django-admin startproject' using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from django.contrib.messages import constants as messages
import logging.config
import os
from django.utils.log import DEFAULT_LOGGING
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-ws_k^45gy*(ptlp!^+7h155j@&&sz9h!d$5gq%4n+=)(eunz)m"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["172.22.26.199", "172.22.26.200", "127.0.0.1", "localhost"]

# DEBUG = False

# ALLOWED_HOSTS = ["*"]


# Application definition
# Load environment variables from .env file
load_dotenv()


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "roster",
    "changeRequest",
    "crispy_forms",
    "crispy_bootstrap4",
    "django_tables2",
    "reporting",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

ROOT_URLCONF = "rms.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "rms.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# -------------------------------------------------------------
# For SQL Lite 3
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }
# -------------------------------------------------------------
# For MySQL
Production_Type = os.getenv("Production_Type")

# Define the default database settings
ubuntu_mysql_database_settings = {
    "ENGINE": "django.db.backends.mysql",
    "OPTIONS": {
        "read_default_file": "/etc/mysql/my.cnf",
    },
}
windows_mysql_database_settings = {
    "ENGINE": "django.db.backends.mysql",
    "NAME": "wfm",
    "USER": "root",
    "PASSWORD": "neaz24x7!",
    "HOST": "",
    "PORT": "3306",
}
# Set DATABASES based on Production_Type
DATABASES = {
    "default": (
        windows_mysql_database_settings
        if Production_Type == "local"
        else ubuntu_mysql_database_settings
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

# AUTH_PASSWORD_VALIDATORS = [
#     {
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Dhaka"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# STATIC_ROOT = os.path.join(PROJECT_ROOT, "static")
STATIC_ROOT = os.path.join(BASE_DIR, "collected_static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.CustomUser"

CRISPY_TEMPLATE_PACK = "bootstrap4"

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "login"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-secondary",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

# Disable Django's logging setup
LOGGING_CONFIG = None

LOGLEVEL = os.environ.get("LOGLEVEL", "info").upper()
# Define the log directory and ensure it exists
log_directory = os.path.join(BASE_DIR, "logs")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                # exact format is not important, this is the minimum information
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
            },
            "django.server": DEFAULT_LOGGING["formatters"]["django.server"],
        },
        "handlers": {
            # console logs to stderr
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "concurrent_log_handler.ConcurrentTimedRotatingFileHandler",
                "formatter": "default",
                "filename": os.path.join(log_directory, "app.log"),  # Base file path
                "when": "M",
                "interval": 1,
                "maxBytes": 0,
                "backupCount": 1440,
                "encoding": "utf-8",
            },
            "django.server": DEFAULT_LOGGING["handlers"]["django.server"],
        },
        "loggers": {
            # default for all undefined Python modules
            "": {
                "level": LOGLEVEL,
                "handlers": [
                    "console",
                    "file",
                ],
            },
            # Our application code
            "app": {
                "level": LOGLEVEL,
                "handlers": [
                    "console",
                    "file",
                ],
                # Avoid double logging because of root logger
                "propagate": False,
            },
            # Prevent noisy modules from logging to Sentry
            "noisy_module": {
                "level": "ERROR",
                "handlers": [
                    "console",
                    "file",
                ],
                "propagate": False,
            },
            # Default runserver request logging
            "django.server": DEFAULT_LOGGING["loggers"]["django.server"],
        },
    }
)


# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "smtp-mail.outlook.com"
# EMAIL_USE_TLS = True
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "iamneazForRMS@outlook.com"
# EMAIL_HOST_PASSWORD = "genex24x7!"
# DEFAULT_FROM_EMAIL = "iamneazForRMS@outlook.com"
# EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
# -------------------------------------------
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_HOST = "172.23.28.31"
# EMAIL_USE_TLS = False
# EMAIL_USE_SSL = False
# EMAIL_PORT = 25
# EMAIL_HOST_USER = "wfm.notification"
# EMAIL_HOST_PASSWORD = "Genex@4312#$"
# DEFAULT_FROM_EMAIL = "wfm.notification@genexsvc.com"
# EMAIL_DOMAIN = "genexservices"
# ---------------------------------------------------
# Enable NTLM authentication
EMAIL_BACKEND = "django_smtp_ntlm_backend.NTLMEmail"
# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_DOMAIN = "genexservices"
EMAIL_HOST = "172.23.28.31"
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
# EMAIL_HOST_USER = "GENEXSVC\wfm.notification"
EMAIL_HOST_USER = "genexservices\wfm.notification"
EMAIL_HOST_PASSWORD = "Genex@4312#$"
DEFAULT_FROM_EMAIL = "wfm.notification@genexsvc.com"
EMAIL_AUTH = (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)

# ------------------------------------------------------
# EMAIL_NTLM_DOMAIN = "genexsvc"  # Replace with your domain name
# EMAIL_NTLM_USERNAME = "wfm.notification"
# EMAIL_NTLM_PASSWORD = "Genex@4312#$"

# EMAIL_BACKEND_OPTIONS = {
#     "host": EMAIL_HOST,
#     "port": 25,
#     "username": EMAIL_NTLM_USERNAME,
#     "password": EMAIL_NTLM_PASSWORD,
#     "ntlm_domain": EMAIL_NTLM_DOMAIN,
# }
# -------------------------------------------------------------
# EMAIL_BACKEND = "rms.utils.exchange_backend.ExchangeEmailBackend"
# EXCHANGE_USERNAME = "wfm.notification@genexsvc.com"
# EXCHANGE_PASSWORD = "Genex@4312#$"
# EXCHANGE_EMAIL = "wfm.notification@genexsvc.com"
# EXCHANGE_SERVER = "172.23.28.31"

DJANGO_TABLES2_TEMPLATE = "django_tables2/bootstrap4.html"
DJANGO_TABLES2_TABLE_ATTRS = {
    "class": "table table-hover",
    "thead": {
        "class": "table-light",
    },
}
