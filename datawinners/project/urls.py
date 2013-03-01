# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.entity.views import edit_subject, disassociate_datasenders

from datawinners.project.wizard_view import create_project, edit_project, reminders, reminder_settings
from datawinners.project.preview_views import sms_preview, web_preview, smart_phone_preview, questionnaire_sms_preview, questionnaire_web_preview
from datawinners.project.submission_views import submissions, project_data, export_data, export_log
from datawinners.project.views import questionnaire, web_questionnaire, create_data_sender_and_web_user, questionnaire_preview, subject_registration_form_preview, sender_registration_form_preview, index, project_overview, subjects, registered_subjects, registered_datasenders, create_reminder, get_reminder, delete_reminder, broadcast_message, manage_reminders, sent_reminders, activate_project, delete_project, undelete_project, review_and_test, edit_subject_questionaire, project_has_data, edit_data_sender,save_questionnaire

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('datawinners.project',),
}

urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    (r'^project/disassociate/$', disassociate_datasenders),
    url(r'^project/questionnaire/(?P<project_id>\w+?)/$', questionnaire, name='questionnaire'),
    url(r'^project/register_subjects/(?P<project_id>\w+?)/$', web_questionnaire, {'subject': True},
        name="subject_questionnaire"),
    url(r'^project/testquestionnaire/(?P<project_id>\w+?)/$', web_questionnaire, name="web_questionnaire"),
    (r'^project/register_datasenders/(?P<project_id>\w+?)/$', create_data_sender_and_web_user),
    url(r'^project/preview/questionnaire/(?P<project_id>\w+?)/$', questionnaire_preview, name="questionnaire_preview"),
    url(r'^project/preview/sms_questionnaire/(?P<project_id>\w+?)/$', questionnaire_preview, {'sms_preview': True},
        name="sms_questionnaire_preview"),
    url(r'^project/preview/subject_registration_form/preview/(?P<project_id>\w+?)/$', subject_registration_form_preview, name="subject_registration_form_preview"),
    url(r'^project/preview/sender_registration_form/preview/(?P<project_id>\w+?)/$', sender_registration_form_preview, name="sender_registration_form_preview"),
    (r'^project/wizard/create/$', create_project),
    url(r'^project/wizard/edit/(?P<project_id>\w+?)/$', edit_project, name="edit_project"),
    (r'^project/questionnaire/save$', save_questionnaire),
    url(r'^project/$', index, name="index"),
    url(r'^project/overview/(?P<project_id>\w+?)/$', project_overview, name="project-overview"),

    url(r'^project/subjects/(?P<project_id>.+?)/$', subjects ,name = "subjects"),
    url(r'^project/registered_subjects/(?P<project_id>.+?)/$', registered_subjects, name = "registered_subjects"),
    (r'^project/subject/edit/(?P<project_id>.+?)/(?P<entity_type>.+?)/(?P<entity_id>.+?)/$', edit_subject),
    url(r'^project/datasenders/(?P<project_id>.+?)/$', create_data_sender_and_web_user, name="create_data_sender_and_web_user"),
    url(r'^project/datasender/edit/(?P<project_id>.+?)/(?P<reporter_id>.+?)/$', edit_data_sender,name="edit_data_sender"),
    url(r'^project/registered_datasenders/(?P<project_id>.+?)/$', registered_datasenders, name="registered_datasenders"),
    (r'^project/create_reminder/(?P<project_id>.+?)/$', create_reminder),
    (r'^project/get_reminder/(?P<project_id>.+?)/$', get_reminder),
    url(r'^project/delete_reminder/(?P<project_id>.+?)/(?P<reminder_id>.+?)/$', delete_reminder, name="delete_reminder"),
    (r'^project/reminderspage/(?P<project_id>.+?)/$', reminders),
    url(r'^project/broadcast_message/(?P<project_id>.+?)/$', broadcast_message, name='broadcast_message'),
    (r'^project/reminders/(?P<project_id>.+?)/$', manage_reminders),
    url(r'^project/sent_reminders/(?P<project_id>.+?)/$', sent_reminders, name='sent_reminders'),
    url(r'^project/set_reminder/(?P<project_id>.+?)/$', reminder_settings, name='reminder_settings'),
    url(r'^project/activate/(?P<project_id>.+?)/$', activate_project, name="activate_project"),
    url(r'^project/delete/(?P<project_id>.+?)/$', delete_project, name="delete_project"),
    (r'^project/undelete/(?P<project_id>.+?)/$', undelete_project),
#    (r'^project/datarecords/filter$', submissions),
    url(r'^project/finish/(?P<project_id>.+?)/$', review_and_test, name='review_and_test'),
    url(r'^project/edit_subjects/(?P<project_id>.+?)/$', edit_subject_questionaire, name = "edit_subject_questionaire"),
    url(r'^project/sms_preview$', sms_preview, name="sms_preview"),
    url(r'^project/web_preview$', web_preview, name="web_preview"),
    url(r'^project/smart_phone_preview$', smart_phone_preview, name="smart_phone_preview"),
    url(r'^project/questionnaire_sms_preview$', questionnaire_sms_preview, name="questionnaire_sms_preview"),
    url(r'^project/questionnaire_web_preview$', questionnaire_web_preview, name="questionnaire_web_preview"),
    url(r'^project/has_submission/(?P<questionnaire_code>[^\\/]+?)/$', project_has_data),

    url(r'^project/(?P<project_id>.+?)/results/(?P<questionnaire_code>.+?)$', submissions, name='submissions'),
    url(r'^project/(?P<project_id>.+?)/data/(?P<questionnaire_code>[^\\/]+?)/$', project_data, name="project_data"),
    (r'^project/export/data$', export_data),
    (r'^project/export/log$', export_log),
)
