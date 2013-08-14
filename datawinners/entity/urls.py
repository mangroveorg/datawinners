# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, url
from datawinners.entity.views import create_data_sender, disassociate_datasenders, associate_datasenders, create_multiple_web_users, edit_subject_questionnaire, save_questionnaire, edit_data_sender, edit_subject
from datawinners.entity.views import create_subject
from datawinners.entity.views import create_type
from datawinners.entity.views import submit
from datawinners.entity.views import all_subject_types, delete_entity, all_subjects, all_subjects_ajax
from datawinners.entity.views import all_datasenders
from datawinners.entity.views import import_subjects_from_project_wizard
from datawinners.entity.views import export_subject
from datawinners.entity.views import export_template

urlpatterns = patterns('',
                       (r'^entity/datasender/create', create_data_sender),
                       (r'^entity/datasender/edit/(?P<reporter_id>.+?)/$', edit_data_sender),
                       (r'^entity/webuser/create', create_multiple_web_users),
                       (r'^entity/subject/create/(?P<entity_type>.+?)/$', create_subject),
                       (r'^entity/subject/edit/(?P<entity_type>.+?)/(?P<entity_id>.+?)/$', edit_subject),
                       (r'^entity/type/create', create_type),
                       (r'^entity/subjects/$', all_subject_types),
                       (r'^entity/subjects/(?P<subject_type>.+?)/ajax/$', all_subjects_ajax),
                       (r'^entity/subjects/(?P<subject_type>.+?)/$', all_subjects),
                       (r'^entity/delete/$', delete_entity),
                       url(r'^entity/datasenders/$', all_datasenders, name='all_datasenders'),
                       (r'^entity/disassociate/$', disassociate_datasenders),
                       (r'^entity/associate/$', associate_datasenders),
                       (r'^entity/subject/import/$', import_subjects_from_project_wizard),
                       (r'^submit$', submit),
                       (r'^entity/subject/edit/(?P<entity_type>.+?)/$', edit_subject_questionnaire),
                       (r'^entity/questionnaire/save$', save_questionnaire),
                       url(r'^entity/subject/export/', export_subject, name="export_subject"),
                       (r'^entity/subject/template/(?P<entity_type>.+?)/$', export_template),
)