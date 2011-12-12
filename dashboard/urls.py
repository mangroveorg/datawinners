# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns

from datawinners.dashboard.views import dashboard, get_submission
from datawinners.dashboard.views import start

urlpatterns = patterns('',
    (r'^dashboard/$', dashboard),
    (r'^start/$', start),
    (r'^submission/breakup/(?P<project_id>.+?)/$', get_submission)
    )
