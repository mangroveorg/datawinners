from django.conf.urls.defaults import patterns, url
from datawinners.entity.view.all_datasenders import AllDataSendersView, AllDataSendersAjaxView, AssociateDataSendersView, DisassociateDataSendersView, delete_data_senders, UsersInSearchedDataSender
from datawinners.entity.view.datasenders import EditDataSenderView
from datawinners.entity.view.datasenders import RegisterDatasenderView
from datawinners.entity.view.datasenders_autocomplete import AllDataSenderAutoCompleteView
from datawinners.entity.view.groups import add_or_remove_contact_from_groups
from datawinners.entity.view.groups import get_group_names, group_ds_count
from datawinners.entity.view.import_template import import_template
from datawinners.entity.view.questionnaires import get_existing_questionnaires
from datawinners.entity.view.send_sms import SendSMS, get_all_mobile_numbers
from datawinners.entity.view.unique_id import delete_subjects
from datawinners.entity.views import create_multiple_web_users, edit_subject_questionnaire, save_questionnaire, edit_subject, get_questionnaire_details_ajax, \
    create_group
from datawinners.entity.views import create_subject, subject_autocomplete
from datawinners.entity.views import create_type
from datawinners.entity.views import all_subject_types, all_subjects, all_subjects_ajax
from datawinners.entity.views import import_subjects_from_project_wizard
from datawinners.entity.views import export_subject
from datawinners.entity.views import delete_subject_types

urlpatterns = patterns('',
                       url(r'datasender/register', RegisterDatasenderView.as_view(), name="register_data_sender"),
                       (r'datasender/edit/(?P<reporter_id>.+?)/$', EditDataSenderView.as_view()),
                       (r'webuser/create', create_multiple_web_users),
                       url(r'subject/create/(?P<entity_type>.+?)/$', create_subject, name='create_subject'),
                       url(r'subject/edit/(?P<entity_type>.+?)/(?P<entity_id>.+?)/$', edit_subject,
                           name="edit_subject"),
                       (r'type/create', create_type),
                       (r'group/create', create_group),
                       (r'subjects/delete/$', delete_subjects),
                       (r'subjects/(?P<subject_type>.+?)/ajax/$', all_subjects_ajax),
                       url(r'subjects/(?P<subject_type>.+?)/$', all_subjects, name="all_subjects"),
                       (r'delete/$', delete_data_senders),
                       url(r'datasenders/$', AllDataSendersView.as_view(), name='all_datasenders'),
                       url(r'datasenders/ajax/$', AllDataSendersAjaxView.as_view(), name="all_datasenders_ajax"),
                       url(r'datasenders/autocomplete/$', AllDataSenderAutoCompleteView.as_view()),
                       url(r'(?P<entity_type>.+?)/autocomplete/$', subject_autocomplete),
                       (r'disassociate/$', DisassociateDataSendersView.as_view()),
                       (r'associate/$', AssociateDataSendersView.as_view()),
                       url(r'subject/import/(?P<form_code>.+?)/$', import_subjects_from_project_wizard,
                           name='import_subjects'),
                       url(r'subject/edit/(?P<entity_type>.+?)/$', edit_subject_questionnaire,
                           name="edit_subject_questionnaire"),
                       (r'subject/details/(?P<entity_type>.+?)/$', get_questionnaire_details_ajax),
                       (r'questionnaire/save$', save_questionnaire),
                       url(r'subject/export/', export_subject, name="export_subject"),
                       url(r'entity/template/(?P<form_code>.+?)/$', import_template, name="import_template"),
                       url(r'subjects/$', all_subject_types, name="all_subject_type_page"),
                       url(r'subject/delete_types', delete_subject_types),
                       url(r'questionnaires/$', get_existing_questionnaires, name="existing_questionnaires"),
                       url(r'superusersindssearched/$', UsersInSearchedDataSender.as_view(), name="superusers_in_ds_searched"),
                       url(r'send-sms/$', SendSMS.as_view(), name="send-sms"),
                       url(r'get-all-mobile-numbers/$', get_all_mobile_numbers, name="get-all-mobile-numbers"),
                       url(r'all-groups/$', get_group_names, name="all_groups"),
                       url(r'update-contact-group/$', add_or_remove_contact_from_groups, name="add_or_remove_contact_from_groups"),
                       url(r'group-ds-count/$', group_ds_count, name="group_ds_count")
)
