# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns

from datawinners.smstester.views import index, tags, tags_opt2

urlpatterns = patterns('',
    (r'^smstester/?$', index),
    (r'^texttags/?$', tags),
    (r'^texttags2/?$', tags_opt2),
                       )
