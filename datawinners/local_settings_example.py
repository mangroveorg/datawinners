# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os

SITE_ID = 1
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'geodjango',                      # Or path to database file if using sqlite3.
        'USER': os.getenv("USER"),                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TRIAL_REGISTRATION_ENABLED = True

HNI_SUPPORT_EMAIL_ID = 'dummy@dummy.com'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.datawinners@gmail.com'
EMAIL_HOST_PASSWORD = 'd@t@winners'
EMAIL_PORT = 587

HNI_BLOG_FEED = 'http://datawinners.wordpress.com/feed/'

WAYBILL_SENT_QUESTIONNAIRE_CODE = 'way1'
WAYBILL_SENT_BY_SITE = 'wbs'
WAYBILL_RECEIVED_QUESTIONNAIRE_CODE = '002'
WAYBILL_RECEIVED_BY_SITE = '003'
WAYBILL_RECEIVED_BY_WH = '004'
SFM_DISTRIBUTION_CODE = '007'
SFE_DISTRIBUTION_CODE = '009'
FFA_DISTRIBUTION_CODE = '010'
PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE = '008'
BILL_OF_LADING_QUESTIONNAIRE_CODE = '015'
BREAK_BULK_SENT_QUESTIONNAIRE_CODE = 'way2'
BREAK_BULK_RECEIVED_PORT_QUESTIONNAIRE_CODE = '016'
CONTAINER_SENT_QUESTIONNAIRE_CODE = 'con'
CONTAINER_RECEIVED_PORT_QUESTIONNAIRE_CODE = '017'
BAV_FFA_CODE = '022'
BAV_SF_CODE = '020'
BAV_CPS_CODE = '018'
NO_OF_RECIPIENT_SFM_CODE = '011'
NO_OF_RECIPIENT_SFE_CODE = '012'
NO_OF_RECIPIENT_FFA_CODE = '013'
NO_OF_RECIPIENT_CPS_CODE = '006'
CPS_DISTRIBUTION_CODE = '005'
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
    'django_extensions',
    'django.contrib.flatpages',
    'south',
    'datawinners.home',
    'datawinners.countrytotrialnumbermapping',
    'datawinners.custom_reports.crs',
    'django_nose',
    'django_digest',
    'django_geoip',
    )

#USE_NEW_VUMI = True
