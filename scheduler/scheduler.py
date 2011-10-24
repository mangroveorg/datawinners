# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
from datetime import date, datetime
from datawinners import  settings
from datawinners.accountmanagement.models import OrganizationSetting, Organization
from datawinners.project.models import Reminder, Project
from datawinners.scheduler.smsclient import SMSClient

import logging
from mangrove.datastore.database import get_db_manager

logger = logging.getLogger("datawinners.reminders")

def send_reminders():
    """
    Entry point for the scheduler. Sends out reminders for the day.
    """
    now = datetime.now()
    send_reminders_scheduled_on(date(now.year, now.month, now.day),SMSClient())

def send_reminders_scheduled_on(on_date,sms_client):
    """
    Sends out reminders scheduled for the given date, for each organization.
    """
    assert isinstance(on_date, date)
    try:
        logger.info("Sending reminders for date:- %s" % on_date)
        for org in Organization.objects.all():
            send_reminders_for_an_organization(org,on_date,sms_client)
        logger.info("Done sending reminders." )
    except Exception as e:
        logger.exception("Exception while sending reminders")

def send_reminders_for_an_organization(org,on_date,sms_client):
    """
    Sends out all reminders for an organization, scheduled for the given date.
    """
    logger.info("Organization %s" % org.name )
    org_setting = OrganizationSetting.objects.filter(organization=org)[0]
#    from_number = org_setting.sms_tel_number
    from_number = org_setting.get_organisation_sms_number()
    dbm = get_db_manager(server=settings.COUCH_DB_SERVER, database=org_setting.document_store)

    # TODO: Below will be replaced by get all projects and each project should have the reminders embedded in them.
    reminders_grouped_by_proj = _get_reminders_grouped_by_project_for_organization(org_setting.organization_id)
    logger.info("Projects with reminders:- %d" % len(reminders_grouped_by_proj) )
    for project_id, reminders in reminders_grouped_by_proj.items():
        project = dbm._load_document(project_id, Project)
        if not project.is_reminder_enabled():
            continue
        send_reminders_on(project,reminders,on_date,sms_client,from_number,dbm)

def send_reminders_on(project,reminders, on_date, sms_client,from_number,dbm):
    """
    Send reminders for the given project, scheduled for the given day.
    """
    assert isinstance(on_date,date)
    logger.info("Project:- %s" % project.name )
    reminders_sent = []
    reminders_to_be_sent = [reminder for reminder in reminders if reminder.should_be_send_on(project.deadline(),on_date) ]
    for reminder in reminders_to_be_sent:
        smses_sent = _send_reminder(from_number,on_date,project,reminder,sms_client,dbm)
        if smses_sent > 0:
            reminders_sent.append(reminder)
            reminder.log(dbm, project.id, on_date, number_of_sms=smses_sent)
    logger.info("Reminders scheduled: %d " % len(reminders_to_be_sent) )
    logger.info("Reminders sent: %d " % len(reminders_sent) )
    return reminders_sent

def _send_reminder(from_number, on_date, project, reminder, sms_client,dbm):
    count = 0
    for datasender in reminder.get_sender_list(project, on_date,dbm):
        sms_sent = sms_client.send_sms(from_number, datasender["mobile_number"], reminder.message)
        if sms_sent:
            count += 1
        logger.info("Reminder sent for %s, Message: %s" % (datasender["mobile_number"],reminder.message,) )
    return count

def _get_reminders_grouped_by_project_for_organization(organization_id):
    reminders_grouped_project_id = defaultdict(list)
    for reminder in Reminder.objects.filter(voided=False,organization=organization_id):
        reminders_grouped_project_id[reminder.project_id].append(reminder)
    return reminders_grouped_project_id

if __name__ == "__main__":
    send_reminders_scheduled_on( date(2011,10,20),SMSClient())

