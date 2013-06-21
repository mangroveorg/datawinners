import os

SITE_ID = 5
DEBUG=False
TEMPLATE_DEBUG=False
COMPRESS = True

ADMINS = (
    ('TW', 'hni-support@thoughtworks.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mangrove',                      # Or path to database file if using sqlite3.
        'USER': 'mangrover',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '178.79.185.35',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

COUCH_DB_SERVER = "http://178.79.185.35:5984"
VUMI_API_URL = "http://178.79.145.58:7000"

COUCHDBMAIN_USERNAME = 'admin'
COUCHDBMAIN_PASSWORD = 'admin'
COUCHDBMAIN_CREDENTIALS = (COUCHDBMAIN_USERNAME, COUCHDBMAIN_PASSWORD)
COUCHDBFEED_USERNAME = 'admin'
COUCHDBFEED_PASSWORD = 'admin'
COUCHDBFEED_CREDENTIALS = (COUCHDBFEED_USERNAME, COUCHDBFEED_PASSWORD)

TRIAL_REGISTRATION_ENABLED = False

FEEDS_ENABLED=True
MAX_FEED_ENTRIES=10000