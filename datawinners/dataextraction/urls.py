from django.conf.urls.defaults import patterns
from datawinners.dataextraction.views import get_for_form, get_unique_id_for_form_code

urlpatterns = patterns('',
    (r'^api/get_for_form/(?P<form_code>\w+?)/$', get_for_form),
    (r'^api/unique-id/(?P<form_code>\w+?)/$', get_unique_id_for_form_code),
    (r'^api/get_for_form/(?P<form_code>\w+?)/(?P<start_date>[-0-9]+?)/$', get_for_form),
    (r'^api/get_for_form/(?P<form_code>\w+?)/(?P<start_date>[-0-9]+?)/(?P<end_date>[-0-9]+?)/$', get_for_form)

)