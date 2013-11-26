from django.conf.urls.defaults import patterns, url
from datawinners.entity.view.all_datasenders import AllDataSendersView, AllDataSendersAjaxView, AssociateDataSendersView, DisassociateDataSendersView, delete_data_senders, UsersInSearchedDataSender
from datawinners.entity.view.datasenders import EditDataSenderView
from datawinners.entity.view.datasenders import DataSenderRegistrationFormView, RegisterDatasenderView
from datawinners.entity.views import create_multiple_web_users, edit_subject_questionnaire, save_questionnaire, edit_subject
from datawinners.entity.views import create_subject
from datawinners.entity.views import create_type
from datawinners.entity.views import all_subject_types, delete_subjects, all_subjects, all_subjects_ajax
from datawinners.entity.views import import_subjects_from_project_wizard
from datawinners.entity.views import export_subject
from datawinners.entity.views import export_template

urlpatterns = patterns('',
                       url(r'datasender/create', DataSenderRegistrationFormView.as_view(), name="create_data_sender"),
                       url(r'datasender/register',RegisterDatasenderView.as_view(),name="register_data_sender"),
                       (r'datasender/edit/(?P<reporter_id>.+?)/$', EditDataSenderView.as_view()),
                       (r'webuser/create', create_multiple_web_users),
                       url(r'subject/create/(?P<entity_type>.+?)/$', create_subject, name='create_subject'),
                       url(r'subject/edit/(?P<entity_type>.+?)/(?P<entity_id>.+?)/$', edit_subject,
                           name="edit_subject"),
                       (r'type/create', create_type),
                       (r'subjects/delete/$', delete_subjects),
                       (r'subjects/(?P<subject_type>.+?)/ajax/$', all_subjects_ajax),
                       url(r'subjects/(?P<subject_type>.+?)/$', all_subjects, name="all_subjects"),
                       (r'delete/$', delete_data_senders),
                       url(r'datasenders/$', AllDataSendersView.as_view(), name='all_datasenders'),
                       url(r'datasenders/ajax/$', AllDataSendersAjaxView.as_view(), name="all_datasenders_ajax"),
                       (r'disassociate/$', DisassociateDataSendersView.as_view()),
                       (r'associate/$', AssociateDataSendersView.as_view()),
                       url(r'subject/import/(?P<form_code>.+?)/$', import_subjects_from_project_wizard,
                           name='import_subjects'),
                       url(r'subject/edit/(?P<entity_type>.+?)/$', edit_subject_questionnaire,
                           name="edit_subject_questionnaire"),
                       (r'questionnaire/save$', save_questionnaire),
                       url(r'subject/export/', export_subject, name="export_subject"),
                       (r'subject/template/(?P<form_code>.+?)/$', export_template),
                       url(r'subjects/$', all_subject_types, name="all_subject_type_page"),
                       url(r'superusersindssearched/$', UsersInSearchedDataSender.as_view(), name="superusers_in_ds_searched")
)