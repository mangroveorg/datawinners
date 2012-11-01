import os

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
        'HOST': '178.79.185.35',                      # Set to empty string for localhost. Not used with sqlite3.
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

COUCH_DB_SERVER = "http://178.79.185.35:5984"
CRS_ORG_ID = 'JHW14178'

LOG_FOLDER = '/var/log/datawinners'
LOG_FILE_NAME = "datawinners.log"
REMINDER_LOG_FILE_NAME = "datawinners_reminders.log"
XFORM_LOG_FILE_NAME = "datawinners_xform.log"
PERFORMANCE_LOG_FILE_NAME = "datawinners-performance.log"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'log-file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join( LOG_FOLDER, LOG_FILE_NAME),
            'mode': 'a', #append+create
        },
        'performance-log-file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join( LOG_FOLDER, PERFORMANCE_LOG_FILE_NAME),
            'mode': 'a', #append+create
        },
        'reminder-log-file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join( LOG_FOLDER, REMINDER_LOG_FILE_NAME),
            'mode': 'a', #append+create
        },
        'xform-log-file': {
            'level': 'INFO',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join( LOG_FOLDER, XFORM_LOG_FILE_NAME),
            'mode': 'a', #append+create
        },
    },
    'loggers': {
        'django': {
            'level':'DEBUG',
            'handlers':['log-file'],
            'propagate': True,
        },
        'performance': {
            'level':'INFO',
            'handlers':['performance-log-file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins','log-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'datawinners.reminders': {
            'level':'INFO',
            'handlers':['reminder-log-file'],
            'propagate': True,
        },
        'datawinners.xform': {
            'level':'INFO',
            'handlers':['xform-log-file'],
            'propagate': True,
        },
        'datawinners.scheduler': {
            'level':'INFO',
            'handlers':['reminder-log-file'],
            'propagate': True,
        },
        'apscheduler.scheduler': {
            'level':'DEBUG',
            'handlers':['reminder-log-file'],
            'propagate': True,
        },
    }
}

HNI_SUPPORT_EMAIL_ID="support@datawinners.com"
HNI_BLOG_FEED = 'http://datawinners.wordpress.com/feed/'
COMPRESS_ENABLED = True