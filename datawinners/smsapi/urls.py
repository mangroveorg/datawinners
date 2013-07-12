from django.conf.urls.defaults import patterns
from datawinners.smsapi.send_sms import send_sms

urlpatterns = patterns('', (r'^sms$', send_sms))
