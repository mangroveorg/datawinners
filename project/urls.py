# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from django.views.generic.simple import direct_to_template

from datawinners.project.views import questionnaire, save_questionnaire, create_profile, project_listing, project_overview, edit_profile, project_results, project_data

urlpatterns = patterns('',
    (r'^project/questionnaire$', questionnaire),
    (r'^project/profile/create$', create_profile),
    (r'^project/profile/edit$', edit_profile),
    (r'^project/questionnaire/save$', save_questionnaire),
    (r'^project/app$', direct_to_template, {'template': 'project/test_application.html'}),
    (r'^project/wizard$', direct_to_template, {'template': 'project/test_wizard.html'}),
    (r'^project/maps$', direct_to_template, {'template': 'project/test_maps.html'}),
    (r'^project/all$', project_listing),
    (r'^project/overview$', project_overview),
    (r'^project/results/(?P<questionnaire_code>.+?)/$', project_results),
    (r'^project/data$',project_data)
    )
