# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns
from datawinners.entity.views import create_datasender
from datawinners.entity.views import create_subject
from datawinners.entity.views import create_type

urlpatterns = patterns('',
    (r'^entity/datasender/create', create_datasender),
    (r'^entity/subject/create', create_subject),
    (r'^entity/type/create', create_type),
)