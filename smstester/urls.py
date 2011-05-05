# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
import datawinners
from datawinners.reports.views import report, hierarchy_report
from datawinners.smstester.views import index

urlpatterns = patterns('',
    (r'^smstester$', index),
)
