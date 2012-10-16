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

LOG_FOLDER = '/home/mangrover/'
LOG_FILE_NAME = "datawinners.log"
REMINDER_LOG_FILE_NAME = "datawinners_reminders.log"
XFORM_LOG_FILE_NAME = "datawinners_xform.log"

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
        'datawinners.reminders': {
            'level':'INFO',
            'handlers':['reminder-log-file'],
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
        'django.request': {
            'handlers': ['mail_admins','log-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'datawinners.xform': {
            'level': 'INFO',
            'handlers': ['xform-log-file'],
            'propagate': True,
        },
    }
}

CRS_ORG_ID = 'BIF126513'