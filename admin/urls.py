# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns
from datawinners.admin.views import register_entity
from datawinners.admin.views import create_entity

urlpatterns = patterns('',
    (r'^admin/entity_management', create_entity),
    (r'^admin/register/entity', register_entity),
)
