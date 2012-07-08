# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.activitylog.views import show_log

urlpatterns = patterns('',
    (r'^useractivity/log/', show_log),
)