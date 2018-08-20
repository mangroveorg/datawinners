# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url

from datawinners.dashboard.views import dashboard, get_submission_breakup, get_submissions_about_project
from datawinners.dashboard.views import start, hide_help_element

urlpatterns = patterns('',
    url(r'^dashboard/$', dashboard, name='dashboard'),
    (r'^dashboard/hide_help_element/$', hide_help_element),
    (r'^start/$', start),
    (r'^submission/breakup/(?P<project_id>.+?)/$', get_submission_breakup),
    (r'^submission/details/(?P<project_id>.+?)/$', get_submissions_about_project)
    )
