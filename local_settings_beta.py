import os

SITE_ID = 5
DEBUG=False
TEMPLATE_DEBUG=False
COMPRESS = False

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

LOG_FOLDER = '/var/log/datawinners'
LOG_FILE_NAME = "datawinners.log"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'log-file': {
            'level': 'ERROR',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join( LOG_FOLDER, LOG_FILE_NAME),
            'mode': 'a', #append+create
        },
    },
    'loggers': {
        'django': {
            'level':'DEBUG',
            'handlers':['log-file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins','log-file'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TRIAL_REGISTRATION_ENABLED = False