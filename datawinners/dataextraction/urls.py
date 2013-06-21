from django.conf.urls.defaults import patterns
from datawinners.dataextraction.views import get_for_subject, get_for_form, get_registered_data

urlpatterns = patterns('',
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_short_code>\w+?)/$', get_for_subject),
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_short_code>\w+?)/(?P<start_date>[-0-9]+?)/$', get_for_subject),
    (r'^api/get_for_subject/(?P<subject_type>\w+?)/(?P<subject_short_code>\w+?)/(?P<start_date>[-0-9]+?)/(?P<end_date>[-0-9]+?)/$', get_for_subject),
    (r'^api/get_for_form/(?P<form_code>\w+?)/$', get_for_form),
    (r'^api/get_for_form/(?P<form_code>\w+?)/(?P<start_date>[-0-9]+?)/$', get_for_form),
    (r'^api/get_for_form/(?P<form_code>\w+?)/(?P<start_date>[-0-9]+?)/(?P<end_date>[-0-9]+?)/$', get_for_form),
    (r'^api/registereddata/(?P<subject_type>\w+?)/((?P<start_date>\d{2}-\d{2}-\d{4})/)?((?P<end_date>\d{2}-\d{2}-\d{4})/)?$', get_registered_data),

)