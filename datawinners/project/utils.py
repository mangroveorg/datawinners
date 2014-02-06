from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.utils import translation
from django.utils.http import urlquote_plus, urlquote
from datawinners.utils import get_organization
from datawinners.project.models import ProjectState, Project
from datawinners.accountmanagement.models import Organization

def make_subject_links(project_id):
    subject_links = {'subjects_link': reverse('registered_subjects', args=[project_id]),
                     'subjects_edit_link': reverse('edit_my_subject_questionnaire', args=[project_id]),
                     'register_subjects_link': reverse('subject_questionnaire', args=[project_id]),
                     'register_subjects_link_web_view': reverse('subject_questionnaire', args=[project_id]) + "?web_view=True",
                     'registered_subjects_link': reverse('registered_subjects', args=[project_id]),
                     'subject_registration_preview_link': reverse('subject_registration_form_preview',
                         args=[project_id])}
    return subject_links

def make_data_sender_links(project_id, reporter_id=None):
    datasender_links = {'datasenders_link': reverse('all_datasenders'),
                        # 'edit_datasender_link': reverse('edit_data_sender', args=[project_id, reporter_id]),
                        'register_datasenders_link': reverse('create_data_sender_and_web_user', args=[project_id]),
                        'registered_datasenders_link': reverse('registered_datasenders', args=[project_id])}
    return datasender_links


def make_project_links(project, questionnaire_code, reporter_id=None):
    project_id = project.id
    project_links = {'overview_link': reverse("project-overview", args=[project_id]),
                     'activate_project_link': reverse("activate_project", args=[project_id]),
                     'delete_project_link': reverse("delete_project", args=[project_id]),
                     'questionnaire_preview_link': reverse("questionnaire_preview", args=[project_id]),
                     'sms_questionnaire_preview_link': reverse("sms_questionnaire_preview", args=[project_id]),
                     'my_datasenders_ajax_link': reverse("my_datasenders_ajax", args=[urlquote(project.name)]),
                     'current_language': translation.get_language()
    }

    if project.state == ProjectState.TEST or project.state == ProjectState.ACTIVE:
        project_links['data_analysis_link'] = reverse("submission_analysis", args=[project_id, questionnaire_code])
        project_links['submission_log_link'] = reverse("submissions", args=[project_id, questionnaire_code])
        project_links['finish_link'] = reverse("review_and_test", args=[project_id])
        project_links['reminders_link'] = reverse('reminder_settings', args=[project_id])

        project_links.update(make_subject_links(project_id))
        project_links.update(make_data_sender_links(project_id, reporter_id))

        project_links['sender_registration_preview_link'] = reverse("sender_registration_form_preview", args=[project_id])
        project_links['sent_reminders_link'] = reverse("sent_reminders", args=[project_id])
        project_links['setting_reminders_link'] = reverse("reminder_settings", args=[project_id])
        project_links['broadcast_message_link'] = reverse("broadcast_message", args=[project_id])
        if 'web' in project.devices:
            project_links['test_questionnaire_link'] = reverse("web_questionnaire", args=[project_id])
        else:
            project_links['test_questionnaire_link'] = ""
    if project.state == ProjectState.ACTIVE:
        project_links['questionnaire_link'] = reverse("questionnaire", args=[project_id])

    return project_links


def project_info(request, manager, form_model, project, questionnaire_code): #revisit:export
    # project = Project.load(manager.database, project_id)
    is_summary_report = form_model.is_entity_type_reporter()
    rp_field = form_model.event_time_question
    organization = get_organization(request)
    in_trial_mode = organization.in_trial_mode
    has_rp = rp_field is not None
    is_monthly_reporting = rp_field.date_format.find('dd') < 0 if has_rp else False

    return {"date_format": rp_field.date_format if has_rp else "dd.mm.yyyy",
            "is_monthly_reporting": is_monthly_reporting, "entity_type": form_model.entity_type[0].capitalize(),
            'project_links': (make_project_links(project, questionnaire_code)),
            'is_quota_reached':is_quota_reached(request, organization=organization),
            'project': project,
            'encoded_project_name': (urlquote(project.name)),
            'import_template_file_name': slugify(project.name),
            'questionnaire_code': questionnaire_code, 'in_trial_mode': in_trial_mode,
            'reporting_period_question_text': rp_field.label if has_rp else None,
            'has_reporting_period': has_rp,
            'is_summary_report': is_summary_report}

def is_quota_reached(request, organization=None, org_id=None):
    if not organization:
        organization = Organization.objects.get(pk=org_id) if org_id else get_organization(request)
    return organization.has_exceeded_submission_limit()
