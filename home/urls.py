# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from django.views.generic.base import TemplateView
from datawinners.home.views import index, switch_language

urlpatterns = patterns('',
        (r'^home/$', index),
        (r'^switch/(?P<language>.{2}?)/$', switch_language),
    )
