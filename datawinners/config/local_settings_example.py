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
VUMI_API_URL = "https://localhost/smstester/vumi-stub"


CRS_ORG_ID = 'TVZ184210'

FEEDS_ENABLED=True
MAX_FEED_ENTRIES=10000

LIMIT_TRIAL_ORG_SUBMISSION_COUNT = 30
LIMIT_TRIAL_ORG_MESSAGE_COUNT = 10
NEAR_SUBMISSION_LIMIT_TRIGGER = 20
NEAR_SMS_LIMIT_TRIGGER = 5
VUMI_API_URL = "http://localhost:2020"

DEBUG_BROWSER="firefox" # firefox | chrome | phantom | ie | htmlunit

GRAPHITE_MONITORING_ENABLED = False
ENVIRONMENT = 'dev'
CARBON_HOST = '127.0.0.1'
CARBON_PORT = 2003