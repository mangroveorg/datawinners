# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.common.lang.views import LanguagesView


urlpatterns = patterns('',
    (r'^languages/', LanguagesView.as_view()),

)
