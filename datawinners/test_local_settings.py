SITE_ID = 4
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'testingdb',                      # Or path to database file if using sqlite3.
        'USER': 'mangrover',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SHOW_GOOGLE_MAPS = False
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
HNI_SUPPORT_EMAIL_ID = 'tester150411@gmail.com'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'test.datawinners@gmail.com'
EMAIL_HOST_PASSWORD = 'd@t@winners'
EMAIL_PORT = 587

WAYBILL_SENT_QUESTIONNAIRE_CODE = 'WBS01'
WAYBILL_RECEIVED_QUESTIONNAIRE_CODE = 'WBR01'
PHYSICAL_INVENTORY_QUESTIONNAIRE_CODE = 'PI01'
CRS_ORG_ID = 'SLX364903'

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
    )
