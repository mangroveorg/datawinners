# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns

from datawinners.project.views import questionnaire, save_questionnaire, create_profile, index, project_overview, edit_profile, project_results, project_data, subjects, export_data, export_log

urlpatterns = patterns('',
        (r'^project/questionnaire/(?P<project_id>.+?)/$', questionnaire),
        (r'^project/profile/create$', create_profile),
        (r'^project/profile/edit/(?P<project_id>.+?)/$', edit_profile),
        (r'^project/questionnaire/save$', save_questionnaire),
        (r'^project/$', index),
        (r'^project/overview/(?P<project_id>.+?)/$', project_overview),
        (r'^project/results/(?P<questionnaire_code>.+?)/$', project_results),
        (r'^project/data/(?P<questionnaire_code>.+?)/$', project_data),
        (r'^project/subjects/(?P<project_id>.+?)/$', subjects),
        (r'^project/export/data$', export_data),
        (r'^project/export/log$', export_log)
)
