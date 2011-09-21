# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
import calendar
from datetime import date, timedelta, datetime
from datawinners import  settings
from datawinners.accountmanagement.models import OrganizationSetting, Organization
from datawinners.project.helper import get_project_data_senders
from datawinners.project.models import Reminder, Project
from datawinners.scheduler.smsclient import SMSClient
from datawinners.scheduler.vumiclient import VumiClient, Connection

import logging
from mangrove.datastore.database import get_db_manager

logger = logging.getLogger("datawinners.reminders")
from mangrove.form_model.form_model import FormModel
from mangrove.transport.reporter import reporters_submitted_data_for_activity_period

def send_reminders():
    """
    Entry point for the scheduler. Sends out reminders for the day.
    """
    send_reminders_scheduled_on(datetime.now(),SMSClient())

def send_reminders_scheduled_on(on_date,sms_client):
    """
    Sends out reminders scheduled for the given date, for each organization.
    """
    try:
        logger.info("Sending reminders for date:- %s" % on_date)
        for org in Organization.objects.all():
            send_reminders_for_an_organization(org,on_date,sms_client)
        logger.info("Done sending reminders." )
    except Exception:
        logger.exception("Exception while sending reminders")

def send_reminders_for_an_organization(org,on_date,sms_client):
    """
    Sends out all reminders for an organization, scheduled for the given date.
    """
    logger.info("Organization %s" % org.name )
    org_setting = OrganizationSetting.objects.filter(organization=org)[0]
    from_number = org_setting.sms_tel_number
    dbm = get_db_manager(server=settings.COUCH_DB_SERVER, database=org_setting.document_store)

    # TODO: Below will be replaced by get all projects and each project should have the reminders embedded in them.
    reminders_grouped_by_proj = _get_reminders_grouped_by_project_for_organization(org_setting.organization_id)
    logger.info("Projects with reminders:- %d" % len(reminders_grouped_by_proj) )
    for project_id, reminders in reminders_grouped_by_proj.items():
        project = dbm._load_document(project_id, Project)
        if not project.is_reminder_enabled():
            continue
        send_reminders_on(project,reminders,on_date,sms_client,from_number,dbm)


def _send_reminder(from_number, on_date, project, reminder, sms_client,dbm):
    count = 0
    datasenders = reminder.get_sender_list(project, on_date,dbm)
    for datasender in datasenders:
        sms_client.send_sms(from_number, datasender["mobile_number"], reminder.message)
        count += 1
        logger.info("Reminder sent for %s, Message: %s" % (datasender["mobile_number"],reminder.message,) )
    return count

def send_reminders_on(project,reminders, on_date, sms_client,from_number,dbm):
    """
    Send reminders for the given project, scheduled for the given day.
    """
    assert isinstance(on_date,date)
    logger.info("Project:- %s" % project.name )
    reminders_sent = []
    reminders_to_be_sent = [ reminder for reminder in reminders if reminder.should_be_send_on(project.deadline(),on_date) ]
    for reminder in reminders_to_be_sent:
        smses_sent = _send_reminder(from_number,on_date,project,reminder,sms_client,dbm)
        if smses_sent > 0: reminders_sent.append(reminder)
    logger.info("Reminders scheduled: %d " % len(reminders_to_be_sent) )
    logger.info("Reminders sent: %d " % len(reminders_sent) )
    return reminders_sent



def _get_reminders_grouped_by_project_for_organization(organization_id):
    reminders = Reminder.objects.filter(voided=False,organization=organization_id)
    reminders_grouped_project_id = defaultdict(list)
    for reminder in reminders:
        reminders_grouped_project_id[reminder.project_id].append(reminder)
    return reminders_grouped_project_id


def _get_last_day_of_month(now):
    return calendar.monthrange(now.year,now.month)[1]

def _send_reminder_to_project_datasenders(dbm, reminder,project):
    logger.info("Sending reminder %s %s for project %s" % ( reminder.day,reminder.reminder_mode, project.name))
    logger.info("Message %s" % ( reminder.message,))
    vumiclient = VumiClient(None, None, connection=Connection("vumi", "vumi", base_url="http://10.253.50.2:7000"))
    datasenders = get_project_data_senders(dbm,project)
    logger.info("Total datasenders for the project: %d" % ( len(datasenders)))
    questionnaire = FormModel.get(dbm, project.qid)
    from_time, end_time = _get_time_period_for_sending_reminders(project.get_reminder_frequency_period())
    logger.info("Time Period Start: %s, Time Period End: %s" % ( from_time,end_time))
    datasenders_who_have_sent = [reporter.value('mobile_number') for reporter in reporters_submitted_data_for_activity_period(dbm, questionnaire.form_code, from_time, end_time)]
    logger.info("Total datasenders who have sent: %d" % ( len(datasenders_who_have_sent)))
    for datasender in datasenders:
        if datasender.get('mobile_number') not in datasenders_who_have_sent:
            logger.info("Sending SMS to %s" % ( datasender.get('mobile_number')))
            vumiclient.send_sms(to_msisdn=datasender.get('mobile_number'),
                                from_msisdn=_get_from_tel_number(reminder)
                                , message=reminder.message)


def _get_from_tel_number(reminder):
    organization_settings = OrganizationSetting.objects.get(organization=reminder.organization)
    return organization_settings.sms_tel_number


def _get_time_period_for_sending_reminders(frequency):
    if frequency == "week":
        from_time = datetime.datetime.now() + timedelta(days=1 - date.today().isoweekday())
        to_time = datetime.datetime.now() + timedelta(days=7 - date.today().isoweekday())
        return from_time, to_time

    if frequency == "month":
        from_time = datetime.datetime(date.today().year, date.today().month, 1)
        to_time = datetime.datetime(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1])
        return from_time, to_time

if __name__ == "__main__":
    send_reminders_scheduled_on( date(2011,9,24),SMSClient())

