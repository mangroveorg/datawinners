# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from alldata.views import data_export, get_entity_list_by_type, get_registered_data
from alldata.views import smart_phone_instruction
from alldata.views import index, reports
from alldata.views import failed_submissions

urlpatterns = patterns('',
    url(r'^alldata/$', index, name = "alldata_index"),
    (r'^alldata/entities/(?P<entity_type>\w+?)/$', get_entity_list_by_type),
    (r'^alldata/registereddata/(?P<subject_type>\w+?)/((?P<start_date>\d{2}-\d{2}-\d{4})/)?((?P<end_date>\d{2}-\d{2}-\d{4})/)?$', get_registered_data),
    (r'^alldata/reports/$', reports),
    (r'^allfailedsubmissions$', failed_submissions),
    (r'^dataexport/$', data_export),
    url(r'^smartphoneinstruction$', smart_phone_instruction, name = "smart_phone_instruction"),
)
