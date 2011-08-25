# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns

from datawinners.home.views import index, secondary

urlpatterns = patterns('',
        (r'^home/$', index),
        (r'^home/secondary/$', secondary),
    )
