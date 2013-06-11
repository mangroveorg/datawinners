# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging
import os
from compress_rotating_file_handler import CompressRotatingFileHandler
logging.handlers.CompressRotatingFileHandler = CompressRotatingFileHandler

BACK_UP_COUNT = 10
MAX_LOG_BYTES = 1024 * 1024 * 50

LOG_FOLDER = '/var/log/datawinners'
LOG_FILE_NAME = "datawinners.log"
REMINDER_LOG_FILE_NAME = "datawinners_reminders.log"
XFORM_LOG_FILE_NAME = "datawinners_xform.log"
PERFORMANCE_LOG_FILE_NAME = "datawinners-performance.log"
WEB_SUBMISSION_LOG_FILE_NAME = "websubmission.log"
SP_SUBMISSION_LOG_FILE_NAME = "sp-submission.log"
COMMANDS_LOG_FILE = "commands.log"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'log-file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.CompressRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, LOG_FILE_NAME),
            'mode': 'a', #append+create
            'formatter': 'verbose',
            'maxBytes': MAX_LOG_BYTES,
            'backupCount': BACK_UP_COUNT
        },
        'performance-log-file': {
            'level': 'INFO',
            'class': 'logging.handlers.CompressRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, PERFORMANCE_LOG_FILE_NAME),
            'mode': 'a', #append+create
            'formatter': 'simple',
            'maxBytes': MAX_LOG_BYTES,
            'backupCount': BACK_UP_COUNT
        },
        'reminder-log-file': {
            'level': 'INFO',
            'class': 'logging.handlers.CompressRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, REMINDER_LOG_FILE_NAME),
            'mode': 'a', #append+create
            'formatter': 'verbose',
            'maxBytes': MAX_LOG_BYTES,
            'backupCount': BACK_UP_COUNT
        },
        'xform-log-file': {
            'level': 'INFO',
            'class': 'logging.handlers.CompressRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, XFORM_LOG_FILE_NAME),
            'mode': 'a', #append+create
            'formatter': 'verbose',
            'maxBytes': MAX_LOG_BYTES,
            'backupCount': BACK_UP_COUNT
        },
        'web-submission': {
            'level': 'INFO',
            'class': 'logging.handlers.CompressRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, WEB_SUBMISSION_LOG_FILE_NAME),
            'mode': 'a', #append+create
            'formatter': 'verbose',
            'maxBytes': MAX_LOG_BYTES,
            'backupCount': BACK_UP_COUNT
        },
        'sp-submission': {
            'level': 'INFO',
            'class': 'logging.handlers.CompressRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, SP_SUBMISSION_LOG_FILE_NAME),
            'mode': 'a', #append+create
            'formatter': 'verbose',
            'maxBytes': MAX_LOG_BYTES,
            'backupCount': BACK_UP_COUNT
        },
        'commands': {
            'level': 'INFO',
            'class': 'logging.handlers.CompressRotatingFileHandler',
            'filename': os.path.join(LOG_FOLDER, COMMANDS_LOG_FILE),
            'mode': 'a', #append+create
            'formatter': 'verbose',
            'maxBytes': MAX_LOG_BYTES,
            'backupCount': BACK_UP_COUNT
        },
    },
    'loggers': {
        'django': {
            'level': 'DEBUG',
            'handlers': ['log-file'],
            'propagate': True,
        },
        'performance': {
            'level': 'INFO',
            'handlers': ['performance-log-file'],
            'propagate': True,
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['log-file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'log-file'],
            'level': 'ERROR',
            'propagate': True,
        },
        'datawinners.reminders': {
            'level': 'INFO',
            'handlers': ['reminder-log-file'],
            'propagate': True,
        },
        'datawinners.xform': {
            'level': 'INFO',
            'handlers': ['xform-log-file'],
            'propagate': True,
        },
        'datawinners.scheduler': {
            'level': 'INFO',
            'handlers': ['reminder-log-file'],
            'propagate': True,
        },
        'apscheduler.scheduler': {
            'level': 'DEBUG',
            'handlers': ['reminder-log-file'],
            'propagate': True,
        },
        'websubmission': {
            'level': 'INFO',
            'handlers': ['web-submission'],
            'propagate': True,
        },
        'spsubmission': {
            'level': 'INFO',
            'handlers': ['sp-submission'],
            'propagate': True,
        },
        'datawinners.main.management.commands': {
            'level': 'INFO',
            'handlers': ['commands'],
            'propagate': True,
        },
        'south': {
            'level': 'ERROR',
            'handlers': ['log-file'],
            'propagate': True,
        },
    }
}
