# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.alldata.views import  get_entity_list_by_type
from datawinners.alldata.views import smart_phone_instruction
from datawinners.alldata.views import index, reports, projects_ajax
from datawinners.alldata.views import failed_submissions, failed_submissions_ajax
from datawinners.alldata.views import export, export_count

urlpatterns = patterns('',
    url(r'^alldata/$', index, name="alldata_index"),
    url(r'^project/$', index),
    url(r'^ajax/project/$', projects_ajax),
    (r'^questionnaire/entities/(?P<entity_type>.+?)/$', get_entity_list_by_type),
    (r'^questionnaire/reports/$', reports),
    (r'^alldata/reports/$', reports),
    (r'^allfailedsubmissions/$', failed_submissions),
    (r'^allfailedsubmissions/ajax/$', failed_submissions_ajax),
    (r'^allfailedsubmissions/export/log$', export),
    (r'^allfailedsubmissions/export/log-count$', export_count),
    url(r'^smartphoneinstruction$', smart_phone_instruction, name="smart_phone_instruction"),
    url(r'^smartphoneinstruction/(?P<project_id>.+?)/$', smart_phone_instruction, name="smart_phone_instruction"),
)
