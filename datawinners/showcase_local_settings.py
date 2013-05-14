import os

SITE_ID = 2
DEBUG = False
TEMPLATE_DEBUG = False
COMPRESS_ENABLED = True
SCHEDULER_HOUR=23
SCHEDULER_MINUTES=30

ADMINS = (
    ('TW', 'apgeorge@thoughtworks.com'),
)

COMPRESS = False

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'geodjango',                      # Or path to database file if using sqlite3.
        'USER': 'jenkins',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

HNI_SUPPORT_EMAIL_ID = 'yadavr@thoughtworks.com'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.datawinners@gmail.com'
EMAIL_HOST_PASSWORD = 'd@t@winners'
EMAIL_PORT = 587

COUCHDBMAIN_USERNAME = 'admin'
COUCHDBMAIN_PASSWORD = 'admin'
COUCHDBMAIN_CREDENTIALS = (COUCHDBMAIN_USERNAME, COUCHDBMAIN_PASSWORD)
COUCHDBFEED_USERNAME = None
COUCHDBFEED_PASSWORD = None
COUCHDBFEED_CREDENTIALS = (COUCHDBFEED_USERNAME, COUCHDBFEED_PASSWORD)

CRS_ORG_ID = 'BIF126513'

FEEDS_ENABLED=False