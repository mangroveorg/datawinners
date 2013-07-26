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

DIGEST_ENFORCE_NONCE_COUNT = False
GEOIP_PATH = "../"

if not DEBUG:
    COMPRESS_DEBUG_TOGGLE = "foo"
MANAGERS = ADMINS

COUCH_DB_SERVER = "http://localhost:5984"
FEEDS_COUCH_SERVER = "http://localhost:6984"
VUMI_USER = "vumi"
VUMI_PASSWORD = "vumi"
REFRESH_RATE = None
USE_NEW_VUMI = False
EDIT_DATA_SENDERS_ENABLED = True
EDIT_SUBJECT_ENABLED = True

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
COMPRESS_ROOT = os.path.join(PROJECT_DIR, 'media')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'
COMPRESS_URL = '/media/'
COMPRESS_PRECOMPILERS = (
    ('text/x-sass', 'sass {infile} {outfile}'),
    ('text/x-scss', 'sass --scss {infile} {outfile}'),
    )


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
    'compressor.finders.CompressorFinder',
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
    'datawinners.middleware.exception_middleware.ExceptionMiddleware',
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
    'datawinners.accountmanagement.context_processors.add_feature_flags',
    )

INDEX_PAGE = '/home'
HOME_PAGE = '/dashboard'
DATASENDER_DASHBOARD = '/alldata/'
LOGIN_REDIRECT_URL = (HOME_PAGE)
TRIAL_EXPIRED_URL = '/trial/expired/'
ACCOUNT_ACTIVATION_DAYS = 7
TRIAL_ACCOUNT_PHONE_NUMBER = ['17752374679', '31658899798', '41798070082']
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'datawinners.accountmanagement',
    'datawinners.activitylog',
    'registration',
    'django.contrib.admin',
    'compressor',
    'datawinners',
    'datawinners.main',
    'datawinners.project',
    'datawinners.dashboard',
    'datawinners.location',
    'datawinners.entity',
    'datawinners.submission',
    'datawinners.xforms',
    'datawinners.dataextraction',
    'django_extensions',
    'django.contrib.flatpages',
    'south',
    'datawinners.home',
    'datawinners.countrytotrialnumbermapping',
    'django_nose',
    'django_digest',
    'datawinners.custom_reports.crs',
    )

WAYBILL_SENT_QUESTIONNAIRE_CODE = 'way1'
WAYBILL_SENT_BY_SITE = 'wbs'
WAYBILL_RECEIVED_QUESTIONNAIRE_CODE = '002'
WAYBILL_RECEIVED_BY_SITE = '003'
WAYBILL_RECEIVED_BY_WH = '004'
SFM_DISTRIBUTION_CODE = '007'
SFE_DISTRIBUTION_CODE = '009'
FFA_DISTRIBUTION_CODE = '010'
PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE = '008'
BILL_OF_LADING_QUESTIONNAIRE_CODE = '015'
BREAK_BULK_SENT_QUESTIONNAIRE_CODE = 'way2'
BREAK_BULK_RECEIVED_PORT_QUESTIONNAIRE_CODE = '016'
CONTAINER_SENT_QUESTIONNAIRE_CODE = 'con'
CONTAINER_RECEIVED_PORT_QUESTIONNAIRE_CODE = '017'
BAV_FFA_CODE = '022'
BAV_SF_CODE = '020'
BAV_CPS_CODE = '018'
NO_OF_RECIPIENT_SFM_CODE = '011'
NO_OF_RECIPIENT_SFE_CODE = '012'
NO_OF_RECIPIENT_FFA_CODE = '013'
NO_OF_RECIPIENT_CPS_CODE = '006'
CPS_DISTRIBUTION_CODE = '005'
PACKING_LIST_QUESTIONNAIRE_CODE = 'pac'

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
            'level': 'DEBUG',
            'propagate': True,
            },
        }
}

SCHEDULER_HOUR = 21
SCHEDULER_MINUTES = 30
API_KEYS = {
    '178.79.163.33:8000': 'ABQIAAAA_DnpC2hsxgPobhTMZQ1NFxT_fiQdjwro1eYvjMeDJdedrin3mBQTAv46jB6-4OUJw7ElbW9r5VyzdA',
    '178.79.161.90': 'AIzaSyA8T3p88UZ-Bqvxmf-L7-6K_eZ4nOYqwcs',
    'localhost:8000': 'ABQIAAAA_DnpC2hsxgPobhTMZQ1NFxRKHMeFb4p-80hFe4LzzFBo1qJpFxQDEP2BqoZSGz3N6EDjkPlXEH_kZQ',
    'www.datawinners.com': 'ABQIAAAAbx2AIcJvKRHLcqmBWwtWdxTjvHtTITV0tzqHG1m2R2AKLO2mQxS0MJ8sZ4h-Ihcm6M7VNjodlrQfTg',
    }

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

GOOGLE_MAPS_ENABLED = True
GOOGLE_ANALYTICS_ENABLED = True
TRIAL_REGISTRATION_ENABLED = True

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
ELASTIC_SEARCH_URL='http://localhost:9200/'

try:
    from local_settings import *
except ImportError, e:
    raise Exception("You need to create a local_settings.py from local_settings_example.py")

from logger_settings import *

