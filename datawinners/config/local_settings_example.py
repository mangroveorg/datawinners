# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os

SITE_ID = 1
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mangrove',                      # Or path to database file if using sqlite3.
        'USER': os.getenv("USER"),                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

API_KEYS = {
    'localhost:8000': 'AIzaSyChwOoz0ZXqQS6EAVcdngeb_17KMLW3eTM'
}

GOOGLE_MAPS_ENABLED = False
GOOGLE_ANALYTICS_ENABLED = False

TRIAL_REGISTRATION_ENABLED = True

HNI_SUPPORT_EMAIL_ID = 'dummy@dummy.com'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.datawinners@gmail.com'
EMAIL_HOST_PASSWORD = 'd@t@winner'
EMAIL_PORT = 587

COUCHDBMAIN_USERNAME = 'admin'
COUCHDBMAIN_PASSWORD = 'admin'
COUCHDBMAIN_CREDENTIALS = (COUCHDBMAIN_USERNAME,COUCHDBMAIN_PASSWORD)
COUCHDBFEED_USERNAME = 'admin'
COUCHDBFEED_PASSWORD = 'admin'
COUCHDBFEED_CREDENTIALS = (COUCHDBFEED_USERNAME,COUCHDBFEED_PASSWORD)

HNI_BLOG_FEED = 'http://datawinners.wordpress.com/feed/'
VUMI_API_URL = "http://localhost:7000"

CRS_ORG_ID = 'TVZ184210'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'datawinners.accountmanagement',
    'datawinners.sms',
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
    'debug_toolbar',
    'rest_framework.authtoken',
    )

DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
    )


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'datawinners.middleware.exception_middleware.ExceptionMiddleware',
    'urlmiddleware.URLMiddleware',
    )

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': lambda x: False,
    'HIDE_DJANGO_SQL': True,
    'TAG': 'p',
    'ENABLE_STACKTRACES' : False,
    }

FEEDS_ENABLED=True
MAX_FEED_ENTRIES=10000

LIMIT_TRIAL_ORG_SUBMISSION_COUNT = 30
LIMIT_TRIAL_ORG_MESSAGE_COUNT = 10
NEAR_SUBMISSION_LIMIT_TRIGGER = 20
NEAR_SMS_LIMIT_TRIGGER = 5
VUMI_API_URL = "http://localhost:2020"