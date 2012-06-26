from django.conf import settings
from django.core import mail

def set_email_settings():
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    settings.DEFAULT_FROM_EMAIL = 'test.datawinners@gmail.com'
    mail.outbox = []