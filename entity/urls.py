# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns
from datawinners.entity.views import create_datasender, disassociate_datasenders, associate_datasenders
from datawinners.entity.views import create_subject
from datawinners.entity.views import create_type
from datawinners.entity.views import submit
from datawinners.entity.views import all_subjects
from datawinners.entity.views import all_datasenders
from datawinners.entity.views import import_subjects_from_project_wizard

urlpatterns = patterns('',
    (r'^entity/datasender/create', create_datasender),
    (r'^entity/subject/create', create_subject),
    (r'^entity/type/create', create_type),
    (r'^entity/subjects/$', all_subjects),
    (r'^entity/datasenders/$', all_datasenders),
    (r'^entity/disassociate/$', disassociate_datasenders),
    (r'^entity/associate/$', associate_datasenders),
    (r'^entity/subject/import/$', import_subjects_from_project_wizard),
    (r'^submit$', submit),
)