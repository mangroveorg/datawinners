# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.common.lang.views import LanguagesView, LanguagesAjaxView


urlpatterns = patterns('',
    (r'^languages/custom_messages', LanguagesAjaxView.as_view()),
    (r'^languages/$', LanguagesView.as_view()),

)
