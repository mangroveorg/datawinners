# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from datawinners.countrytotrialnumbermapping.views import trial_account_phone_numbers

urlpatterns = patterns('',
    (r'^(?P<language>.{2}?)/your-account-phone-number/$', trial_account_phone_numbers),
)