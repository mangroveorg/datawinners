# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url
from datawinners.entity.view.all_datasenders import DisassociateDataSendersView
from datawinners.project.views.change_language import QuestionnaireLanguageView
from datawinners.project.views.create_questionnaire import create_project
from datawinners.project.views.datasenders import MyDataSendersAjaxView, registered_datasenders
from datawinners.project.views.import_submissions_views import ImportSubmissionView

from datawinners.project.wizard_view import edit_project, reminder_settings, get_templates, get_template_details
from datawinners.project.preview_views import sms_preview, web_preview, smart_phone_preview
from datawinners.project.views import submission_views
from datawinners.project.views.views import questionnaire, create_data_sender_and_web_user, questionnaire_preview, subject_registration_form_preview, sender_registration_form_preview, project_overview, \
    registered_subjects, broadcast_message, sent_reminders, delete_project, undelete_project, edit_my_subject_questionnaire, project_has_data, subject_web_questionnaire, survey_web_questionnaire, edit_my_subject, get_questionnaire_ajax, \
    rename_project, change_ds_group

js_info_dict = {
    'domain': 'djangojs',
    'packages': ('datawinners.project',),
}
urlpatterns = patterns('',
                       (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
                       (r'^project/disassociate/$', DisassociateDataSendersView.as_view()),
                       url(r'^project/questionnaire/(?P<project_id>\w+?)/$', questionnaire, name='questionnaire'),
                       url(r'^project/questionnaire/ajax/(?P<project_id>\w+?)/$', get_questionnaire_ajax, name='questionnaire_ajax'),
                       url(r'^project/register_subjects/(?P<project_id>\w+?)/entity/(?P<entity_type>.+?)/$', subject_web_questionnaire,
                           name="subject_questionnaire"),
                       url(r'^project/testquestionnaire/(?P<project_id>\w+?)/$', survey_web_questionnaire,
                           name="web_questionnaire"),
                       (r'^project/register_datasenders/(?P<project_id>\w+?)/$', create_data_sender_and_web_user),
                       url(r'^project/preview/questionnaire/(?P<project_id>\w+?)/$', questionnaire_preview,
                           name="questionnaire_preview"),
                       url(r'^project/preview/sms_questionnaire/(?P<project_id>\w+?)/$', questionnaire_preview,
                           {'sms_preview': True}, name="sms_questionnaire_preview"),
                       url(r'^project/preview/subject_registration_form/preview/(?P<project_id>\w+?)/entity/(?P<entity_type>.+?)/$',
                           subject_registration_form_preview, name="subject_registration_form_preview"),
                       url(r'^project/preview/sender_registration_form/preview/(?P<project_id>\w+?)/$',
                           sender_registration_form_preview, name="sender_registration_form_preview"),
                       url(r'^project/wizard/create/$', create_project, name="create_project"),
                       (r'^project/template/(?P<template_id>\w+?)/$', get_template_details),
                       url(r'^project/templates/$', get_templates, name="project_templates"),
                       url(r'^project/wizard/edit/(?P<project_id>\w+?)/$', edit_project, name="edit_project"),
                       url(r'^project/overview/(?P<project_id>\w+?)/$', project_overview, name="project-overview"),
                       url(r'^project/language/(?P<project_id>\w+?)/$', QuestionnaireLanguageView.as_view(), name="project-language"),
                       url(r'^project/registered_subjects/(?P<project_id>\w+?)/$', registered_subjects,
                           name="registered_subjects_default"),
                       url(r'^project/registered_subjects/(?P<project_id>\w+?)/entity/(?P<entity_type>.+?)/$', registered_subjects,
                           name="registered_subjects"),
                       url(r'^project/subject/edit/(?P<project_id>.+?)/(?P<entity_type>.+?)/(?P<entity_id>.+?)/$',
                           edit_my_subject, name="edit_my_subject"),
                       url(r'^project/datasenders/(?P<project_id>.+?)/$', create_data_sender_and_web_user,
                           name="create_data_sender_and_web_user"),
                       url(r'^project/registered_datasenders/(?P<project_id>.+?)/$', registered_datasenders,
                           name="registered_datasenders"),
                       url(r'^project/(?P<project_name>.+?)/registered_datasenders/ajax/$',
                           MyDataSendersAjaxView.as_view(), name="my_datasenders_ajax"),
                       url(r'^project/broadcast_message/(?P<project_id>.+?)/$', broadcast_message,
                           name='broadcast_message'),
                       url(r'^project/sent_reminders/(?P<project_id>.+?)/$', sent_reminders, name='sent_reminders'),
                       url(r'^project/set_reminder/(?P<project_id>.+?)/$', reminder_settings, name='reminder_settings'),
                       url(r'^project/delete/(?P<project_id>.+?)/$', delete_project, name="delete_project"),
                       (r'^project/rename/(?P<project_id>.+?)$', rename_project),
                       (r'^project/undelete/(?P<project_id>.+?)/$', undelete_project),
                       url(r'^project/edit_subjects/(?P<project_id>.+?)/entity/(?P<entity_type>.+?)/$', edit_my_subject_questionnaire,
                           name="edit_my_subject_questionnaire"),
                       url(r'^project/sms_preview$', sms_preview, name="sms_preview"),
                       url(r'^project/web_preview$', web_preview, name="web_preview"),
                       url(r'^project/smart_phone_preview$', smart_phone_preview, name="smart_phone_preview"),
                       url(r'^project/has_submission/(?P<questionnaire_code>[^\\/]+?)/$', project_has_data),
                       url(r'^project/(?P<project_id>.+?)/results/(?P<questionnaire_code>.+?)/tab/(?P<tab>[^\\/]+?)/$',
                           submission_views.index),
                       url(r'^project/(?P<project_id>.+?)/results/(?P<questionnaire_code>.+?)/$',
                           submission_views.index, name='submissions'),
                       url(r'^project/(?P<project_id>.+?)/data/(?P<questionnaire_code>[^\\/]+?)/$',
                           submission_views.analysis_results, name="submission_analysis"),
                       url(r'^project/(?P<project_id>.+?)/submissions/edit/(?P<survey_response_id>[^\\/]+?)/$',
                           submission_views.edit, name="submissions_edit"),
                       url(
                           r'^project/(?P<project_id>.+?)/submissions/edit/(?P<survey_response_id>[^\\/]+?)/tab/(?P<tab>[^\\/]+?)/$',
                           submission_views.edit, name="submissions_edit"),
                       url(r'^project/(?P<project_id>.+?)/submissions/delete/$', submission_views.delete,
                           name="submissions_delete"),
                       (r'^project/export/log$', submission_views.export),
                       (r'^project/submissions/(?P<form_code>.+?)/headers$', submission_views.headers),
                       (r'^project/submissions/(?P<form_code>.+?)/analysis$', submission_views.get_stats),
                       (r'^project/submissions/(?P<form_code>.+?)$', submission_views.get_submissions),
                       url(r'^project/import-submissions/(?P<form_code>.+?)$', ImportSubmissionView.as_view(), name="import_submissions"),
                       url(r'^project/change-group/$', change_ds_group),
                       )

