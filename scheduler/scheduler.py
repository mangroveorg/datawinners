# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
import calendar
from datetime import date, timedelta, datetime
from datawinners import utils
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.project.helper import get_project_data_senders
from datawinners.project.models import Reminder, Project
from datawinners.scheduler.vumiclient import Client, Connection

import logging
logger = logging.getLogger("datawinners.reminders")
from mangrove.form_model.form_model import FormModel
from mangrove.transport.reporter import reporters_submitted_data
from mangrove.utils.dates import convert_to_epoch


def send_reminders():
    try:
        logger.info("Sending reminders")
        reminders_grouped_project_id = _get_reminders_grouped_by_project()

        for project_id, reminders in reminders_grouped_project_id.items():
            dbm = utils.get_database_manager_for_org(reminders[0].organization)
            project = dbm._load_document(project_id, Project)
            if not project.is_reminder_enabled():
                continue
            logger.info("Total %d reminders for project %s" % (len(reminders),project.name ))
            for reminder in reminders:
                if _should_send_reminder(reminder, project):
                    _send_reminder_to_project_datasenders(dbm, reminder,project)
    except Exception:
        logger.exception("Exception while sending reminders")



def _get_reminders_grouped_by_project():
    reminders = Reminder.objects.filter(voided=False)
    reminders_grouped_project_id = defaultdict(list)
    for reminder in reminders:
        reminders_grouped_project_id[reminder.project_id].append(reminder)
    return reminders_grouped_project_id

def _get_last_day_of_month(now):
    return calendar.monthrange(now.year,now.month)[1]

#FIXME This should be encapsulated in the Projects model, but holding this work until we the functionality of the
#feature is finalized with client.
def _should_send_reminder(reminder, project):
    current_date = date.today()
    current_day=current_date.day
    if project.get_reminder_frequency_period()=="month":
        if reminder.reminder_mode == "on_deadline":
            if current_day == project.get_deadline_day():
                return True
        if reminder.reminder_mode == "before_deadline":
            if current_day == (project.get_deadline_day() - reminder.day):
                return True
        if reminder.reminder_mode == "after_deadline":
            if current_day == (project.get_deadline_day() + reminder.day):
                return True

def _send_reminder_to_project_datasenders(dbm, reminder,project):
    logger.info("Sending reminder %s %s for project %s" % ( reminder.day,reminder.reminder_mode, project.name))
    logger.info("Message %s" % ( reminder.message,))
    vumiclient = Client(None, None, connection=Connection("vumi", "vumi", base_url="http://10.253.50.2:7000"))
    datasenders = get_project_data_senders(dbm,project)
    logger.info("Total datasenders for the project: %d" % ( len(datasenders)))
    questionnaire = FormModel.get(dbm, project.qid)
    from_time, end_time = _get_time_period_for_sending_reminders(project.get_reminder_frequency_period())
    logger.info("Time Period Start: %s, Time Period End: %s" % ( from_time,end_time))
    datasenders_who_have_sent = [reporter.value('mobile_number') for reporter in reporters_submitted_data(dbm, questionnaire.form_code, from_time, end_time)]
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
        return convert_to_epoch(from_time), convert_to_epoch(to_time)

    if frequency == "month":
        from_time = datetime.datetime(date.today().year, date.today().month, 1)
        to_time = datetime.datetime(date.today().year, date.today().month, calendar.monthrange(date.today().year, date.today().month)[1])
        return convert_to_epoch(from_time), convert_to_epoch(to_time)

if __name__ == "__main__":
    print "main"
    send_reminders()