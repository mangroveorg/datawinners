# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.conf.urls.defaults import patterns, url

from datawinners.project.views import questionnaire_wizard, save_questionnaire, create_profile, index, project_overview,\
    edit_profile, project_results, project_data, subjects_wizard, datasenders, export_data, export_log, activate_project, finish, subjects, datasenders_wizard, registered_subjects, registered_datasenders, questionnaire, questionnaire_preview, submissions, subject_registration_form_preview, sender_registration_form_preview, test_questionnaire, reminders_wizard, enable_reminders_in_project, reminders

urlpatterns = patterns('',
        (r'^project/wizard/questionnaire/(?P<project_id>.+?)/$', questionnaire_wizard),
        (r'^project/questionnaire/(?P<project_id>.+?)/$', questionnaire),
        (r'^project/testquestionnaire/(?P<project_id>.+?)/$', test_questionnaire),
        (r'^project/preview/questionnaire/(?P<project_id>.+?)/$', questionnaire_preview),
        (r'^project/preview/subject_registration_form/preview/(?P<project_id>.+?)/$', subject_registration_form_preview),
        (r'^project/preview/sender_registration_form/preview/(?P<project_id>.+?)/$', sender_registration_form_preview),
        (r'^project/wizard/create$', create_profile),
        (r'^project/wizard/edit/(?P<project_id>.+?)/$', edit_profile),
        (r'^project/questionnaire/save$', save_questionnaire),
        (r'^project/$', index),
                       url(r'^project/overview/(?P<project_id>.+?)/$', project_overview, name="project-overview"),
        (r'^project/(?P<project_id>.+?)/results/(?P<questionnaire_code>.+?)/$', project_results),
        (r'^project/(?P<project_id>.+?)/data/(?P<questionnaire_code>.+?)/$', project_data),
        (r'^project/wizard/subjects/(?P<project_id>.+?)/$', subjects_wizard),
        (r'^project/subjects/(?P<project_id>.+?)/$', subjects),
        (r'^project/registered_subjects/(?P<project_id>.+?)/$', registered_subjects),
        (r'^project/datasenders/(?P<project_id>.+?)/$', datasenders),
        (r'^project/registered_datasenders/(?P<project_id>.+?)/$', registered_datasenders),
        (r'^project/wizard/reminders/(?P<project_id>.+?)/$', reminders_wizard),
        (r'^project/reminders/(?P<project_id>.+?)/$', reminders),
        (r'^project/reminderstatus/(?P<project_id>.+?)/$', enable_reminders_in_project),
        (r'^project/wizard/datasenders/(?P<project_id>.+?)/$', datasenders_wizard),
        (r'^project/activate/(?P<project_id>.+?)/$', activate_project),
        (r'^project/wizard/finish/(?P<project_id>.+?)/$', finish),
        (r'^project/export/data$', export_data),
        (r'^project/export/log$', export_log),
        (r'^project/datarecords/filter$', submissions)

)
