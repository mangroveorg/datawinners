# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns
from datawinners.subjects.views import index, import_subjects_from_project_wizard


urlpatterns = patterns('',
        (r'^subjects/$', index),
        (r'^import/$', import_subjects_from_project_wizard),
                       )
