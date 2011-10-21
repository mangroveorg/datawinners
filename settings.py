    # vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

# Django settings for web project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_DIR = os.path.dirname(__file__)

EXPIRED_DAYS_FOR_TRIAL_ACCOUNT = 30

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS


COUCH_DB_SERVER = "http://localhost:5984"
VUMI_API_URL = "http://178.79.161.90:7000"
VUMI_USER = "vumi"
VUMI_PASSWORD = "vumi"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = None

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
LANGUAGES = (
                ('en', 'English'),
                ('fr', 'French'),
            )


# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = ')(qag8n#2$8dl8krz20+xe9khly2_g$k&29m&-$)bcmd-l-5m)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'datawinners.urls'
AUTH_PROFILE_MODULE = "accountmanagement.NGOUserProfile"

TEMPLATE_DIRS = (
#    os.path.join(PROJECT_DIR, 'registration'),
    os.path.join(PROJECT_DIR, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/registration".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'accountmanagement.context_processors.add_feature_flags',
)

HOME_PAGE = '/dashboard'
DATASENDER_DASHBOARD = '/alldata/'
LOGIN_REDIRECT_URL = (HOME_PAGE)
TRIAL_EXPIRED_URL = '/trial/expired/'
ACCOUNT_ACTIVATION_DAYS = 7

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'datawinners.accountmanagement',
    'registration',
    'django.contrib.admin',
    'compressor',
    'datawinners.main',
    'datawinners.project',
    'datawinners.dashboard',
    'datawinners.location',
    'datawinners.entity',
    'datawinners.submission',
    'django_extensions',
    'django.contrib.flatpages',
    'south',
    'datawinners.home',
    'django_nose'
)

COMPILER_FORMATS = {
    '.sass': {
        'binary_path': 'sass',
        'arguments': '*.sass *.css'
    },
    '.scss': {
        'binary_path': 'sass',
        'arguments': '*.scss *.css'
    }
}
COMPRESS = False

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.datawinners@gmail.com'
EMAIL_HOST_PASSWORD = 'd@t@winners'
EMAIL_PORT = 587

SCHEDULER_HOUR=21
SCHEDULER_MINUTES=34
api_keys = {
    '178.79.163.33:8000': 'ABQIAAAA_DnpC2hsxgPobhTMZQ1NFxT_fiQdjwro1eYvjMeDJdedrin3mBQTAv46jB6-4OUJw7ElbW9r5VyzdA',
    '178.79.161.90:8000': 'ABQIAAAA_DnpC2hsxgPobhTMZQ1NFxTR2RUVwe-S02pZ76sdA7VcVHTvQRTv5NLP3k1Sw_fi4D6iIeholKIHKg',
    'localhost:8000': 'ABQIAAAA_DnpC2hsxgPobhTMZQ1NFxRKHMeFb4p-80hFe4LzzFBo1qJpFxQDEP2BqoZSGz3N6EDjkPlXEH_kZQ',#We don't really need it
    'www.datawinners.com': 'ABQIAAAAbx2AIcJvKRHLcqmBWwtWdxTjvHtTITV0tzqHG1m2R2AKLO2mQxS0MJ8sZ4h-Ihcm6M7VNjodlrQfTg'}

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

USE_ORDERED_SMS_PARSER = False
TRIAL_REGISTRATION_ENABLED = True

try:
    from local_settings import *
except ImportError, e:
    raise Exception("You need to create a local_settings.py from local_settings_example.py")
