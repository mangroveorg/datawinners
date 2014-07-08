# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.alldata.views import  get_entity_list_by_type
from datawinners.alldata.views import smart_phone_instruction
from datawinners.alldata.views import index, reports
from datawinners.alldata.views import failed_submissions

urlpatterns = patterns('',
    url(r'^alldata/$', index, name="alldata_index"),
    (r'^questionnaire/entities/(?P<entity_type>.+?)/$', get_entity_list_by_type),
    (r'^alldata/reports/$', reports),
    (r'^allfailedsubmissions/$', failed_submissions),
    url(r'^smartphoneinstruction$', smart_phone_instruction, name="smart_phone_instruction"),
    url(r'^smartphoneinstruction/(?P<project_id>.+?)/$', smart_phone_instruction, name="smart_phone_instruction"),
)
