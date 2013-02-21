# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from alldata.views import  get_entity_list_by_type
from alldata.views import smart_phone_instruction
from alldata.views import index, reports
from alldata.views import failed_submissions

urlpatterns = patterns('',
    url(r'^alldata/$', index, name = "alldata_index"),
    (r'^alldata/entities/(?P<entity_type>.+?)/$', get_entity_list_by_type),
    (r'^alldata/reports/$', reports),
    (r'^allfailedsubmissions$', failed_submissions),
    url(r'^smartphoneinstruction$', smart_phone_instruction, name = "smart_phone_instruction"),
)
