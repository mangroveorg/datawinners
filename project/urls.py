# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from django.views.generic.simple import direct_to_template
from datawinners.project.views import questionnaire,save_questionnaire,set_up_questionnaire

urlpatterns = patterns('',
    (r'^project/questionnaire$', questionnaire),
    (r'^project/setup$', set_up_questionnaire),
    (r'^project/questionnaire/save$',save_questionnaire),
    (r'^project/app$',direct_to_template,{'template':'project/test_application.html'}),
    (r'^project/wizard$',direct_to_template,{'template':'project/test_wizard.html'})
)