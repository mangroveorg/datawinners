# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
from datetime import date, datetime
import logging

from datawinners.accountmanagement.models import OrganizationSetting, Organization
from datawinners.project.models import Project, get_reminder_repository
from datawinners.scheduler.smsclient import SMSClient
from datawinners.main.database import get_db_manager
from dateutil.relativedelta import relativedelta
from datawinners.accountmanagement.utils import RELATIVE_DELTA_BY_EMAIL_TYPE


logger = logging.getLogger("datawinners.reminders")


def send_reminders():
    """
    Entry point for the scheduler. Sends out reminders for the day.
    """
    now = datetime.now()
    send_reminders_scheduled_on(date(now.year, now.month, now.day), SMSClient())


def _get_paid_organization():
    return Organization.objects.filter(in_trial_mode=False)


def send_reminders_scheduled_on(on_date, sms_client):
    """
    Sends out reminders scheduled for the given date, for each organization.
    """
    assert isinstance(on_date, date)

    try:
        logger.info("Sending reminders for date:- %s" % on_date)
        paid_organization = _get_paid_organization()
        for org in paid_organization:
            logger.info("Organization %s" % org.name)
            org_setting = OrganizationSetting.objects.filter(organization=org)[0]
            manager = get_db_manager(org_setting.document_store)
            send_reminders_for_an_organization(org, on_date, sms_client, from_number=org_setting.sms_tel_number,
                                               dbm=manager)
        logger.info("Done sending reminders.")
    except Exception as e:
        logger.exception("Exception while sending reminders")


def send_reminders_for_an_organization(org, on_date, sms_client, from_number, dbm):
    """
    Sends out all reminders for an organization, scheduled for the given date.
    """
    reminders_grouped_by_proj = _get_reminders_grouped_by_project_for_organization(org.org_id)
    logger.info("Projects with reminders:- %d" % len(reminders_grouped_by_proj))
    for project_id, reminders in reminders_grouped_by_proj.items():
        project = dbm._load_document(project_id, Project)
        if not project.has_deadline():
            continue
            #send reminders to next projects in the queue if their is any error while sending reminders to previous project
        try:
            _, total_sms_sent = send_reminders_on(project, reminders, on_date, sms_client, from_number, dbm)
            org.increment_all_message_count_by(0, total_sms_sent)
        except Exception:
            logger.exception("Exception while sending reminders for this project")


def send_reminders_on(project, reminders, on_date, sms_client, from_number, dbm):
    """
    Send reminders for the given project, scheduled for the given day.
    """
    assert isinstance(on_date, date)
    logger.info("Project:- %s" % project.name)
    reminders_sent = []
    total_sent = 0
    reminders_to_be_sent = [reminder for reminder in reminders if
                            reminder.should_be_send_on(project.deadline(), on_date)]
    for reminder in reminders_to_be_sent:
        #send next reminder if their is any error in sending reminder
        smses_sent = 0
        try:
            smses_sent = sms_client.send_reminder(from_number, on_date, project, reminder, dbm)
        except Exception:
            logger.exception("Exception while sending Reminder")

        if smses_sent > 0:
            total_sent += smses_sent
            reminders_sent.append(reminder)
    logger.info("Reminders scheduled: %d " % len(reminders_to_be_sent))
    logger.info("Reminders sent: %d " % len(reminders_sent))
    return reminders_sent, total_sent


def _get_reminders_grouped_by_project_for_organization(organization_id):
    reminders_grouped_project_id = defaultdict(list)
    for reminder in get_reminder_repository().get_all_reminders_for(organization_id):
        reminders_grouped_project_id[reminder.project_id].append(reminder)
    return reminders_grouped_project_id

def send_time_based_reminder_email():
    for email_type, delta_dict in RELATIVE_DELTA_BY_EMAIL_TYPE.items():
        active_date = datetime.strftime(datetime.now() - relativedelta(**delta_dict[0]), "%Y-%m-%d")
        organizations = Organization.get_all_trial_organizations(active_date__contains=active_date)
        for organization in organizations:
            if organization.active_date != organization.status_changed_datetime and not delta_dict[1]: continue
            organization.send_mail_to_organization_creator(email_type)

if __name__ == "__main__":
    #send_reminders_scheduled_on(date(2011, 10, 20), SMSClient())
    send_time_based_reminder_email()

