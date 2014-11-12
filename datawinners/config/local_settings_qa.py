SITE_ID = 6
DEBUG=False


ADMINS = (('DWBLR', 'datawinnersblr@thoughtworks.com'),)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mangrove',                      # Or path to database file if using sqlite3.
        'USER': 'mangrover',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

API_KEYS = {
    '172.18.9.6': 'AIzaSyDE7V6tcY34e5uAB7eYS7AcSStty87vulQ'
}

GOOGLE_ANALYTICS_ENABLED = False

TRIAL_REGISTRATION_ENABLED = True
GOOGLE_MAPS_ENABLED = True
HNI_SUPPORT_EMAIL_ID = 'datawinnersblr@thoughtworks.com'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.datawinners@gmail.com'
EMAIL_HOST_PASSWORD = 'd@t@winner'
EMAIL_PORT = 587

COUCHDBMAIN_USERNAME = 'admin'
COUCHDBMAIN_PASSWORD = 'admin'
COUCHDBMAIN_CREDENTIALS = (COUCHDBMAIN_USERNAME, COUCHDBMAIN_PASSWORD)
COUCHDBFEED_USERNAME = 'admin'
COUCHDBFEED_PASSWORD = 'admin'
COUCHDBFEED_CREDENTIALS = (COUCHDBFEED_USERNAME, COUCHDBFEED_PASSWORD)

HNI_BLOG_FEED = 'http://hni.org/blog/category/datawinners-data-collection-for-development/feed/'

CRS_ORG_ID = 'TVZ184210'

FEEDS_ENABLED = True
MAX_FEED_ENTRIES=100
LIMIT_TRIAL_ORG_SUBMISSION_COUNT = 30
LIMIT_TRIAL_ORG_MESSAGE_COUNT = 10
NEAR_SUBMISSION_LIMIT_TRIGGER = 20
NEAR_SMS_LIMIT_TRIGGER = 5
VUMI_API_URL = "https://localhost/smstester/vumi-stub"
