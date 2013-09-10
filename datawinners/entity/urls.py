# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, url
from datawinners.entity.views import create_data_sender, disassociate_datasenders, associate_datasenders, create_multiple_web_users, edit_subject_questionnaire, save_questionnaire, edit_data_sender, edit_subject
from datawinners.entity.views import create_subject
from datawinners.entity.views import create_type
from datawinners.entity.views import all_subject_types, delete_data_senders, delete_subjects, all_subjects, all_subjects_ajax
from datawinners.entity.views import all_datasenders
from datawinners.entity.views import import_subjects_from_project_wizard
from datawinners.entity.views import export_subject
from datawinners.entity.views import export_template

urlpatterns = patterns('',
                       (r'datasender/create', create_data_sender),
                       (r'datasender/edit/(?P<reporter_id>.+?)/$', edit_data_sender),
                       (r'webuser/create', create_multiple_web_users),
                       url(r'subject/create/(?P<entity_type>.+?)/$', create_subject, name='create_subject'),
                       url(r'subject/edit/(?P<entity_type>.+?)/(?P<entity_id>.+?)/$', edit_subject, name="edit_subject"),
                       (r'type/create', create_type),
                       (r'subjects/delete/$', delete_subjects),
                       (r'subjects/(?P<subject_type>.+?)/ajax/$', all_subjects_ajax),
                       url(r'subjects/(?P<subject_type>.+?)/$', all_subjects, name="all_subjects"),
                       (r'delete/$', delete_data_senders),
                       url(r'datasenders/$', all_datasenders, name='all_datasenders'),
                       (r'disassociate/$', disassociate_datasenders),
                       (r'associate/$', associate_datasenders),
                       url(r'subject/import/(?P<form_code>.+?)/$', import_subjects_from_project_wizard,
                           name='import_subjects'),
                       url(r'subject/edit/(?P<entity_type>.+?)/$', edit_subject_questionnaire,
                           name="edit_subject_questionnaire"),
                       (r'questionnaire/save$', save_questionnaire),
                       url(r'subject/export/', export_subject, name="export_subject"),
                       (r'subject/template/(?P<entity_type>.+?)/$', export_template),
                       url(r'subjects/$', all_subject_types, name="all_subject_type_page"),
)