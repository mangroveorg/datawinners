SITE_ID = 5
DEBUG=False
TEMPLATE_DEBUG=DEBUG

ADMINS = (
    ('TW', 'support@datawinners.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'mangrove',                      # Or path to database file if using sqlite3.
        'USER': 'mangrover',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'no-reply@datawinners.com'
EMAIL_HOST_PASSWORD = 'Amelia44'
EMAIL_PORT = 587


SCHEDULER_HOUR=01
SCHEDULER_MINUTES=00

VUMI_API_URL = "http://178.79.145.58:7000"
VUMI_USER = "airtel_mada"
VUMI_PASSWORD = "airtel_mada"

COUCH_DB_SERVER = "http://localhost:5984"
CRS_ORG_ID = 'JHW14178'

COUCHDBMAIN_USERNAME = 'admin'
COUCHDBMAIN_PASSWORD = 'HN1b@ngl0r3ma1n'
COUCHDBMAIN_CREDENTIALS = (COUCHDBMAIN_USERNAME, COUCHDBMAIN_PASSWORD)
COUCHDBFEED_USERNAME = None
#when populated should be HN1b@ngl0r3f33d
COUCHDBFEED_PASSWORD = None
COUCHDBFEED_CREDENTIALS = (COUCHDBFEED_USERNAME, COUCHDBFEED_PASSWORD)

HNI_SUPPORT_EMAIL_ID="support@datawinners.com"
HNI_BLOG_FEED = 'http://datawinners.wordpress.com/feed/'
COMPRESS_ENABLED = True

FEEDS_ENABLED=False