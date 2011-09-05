# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
import calendar
from datetime import date
from datawinners import utils
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.entity.import_data import load_all_subjects_of_type
from datawinners.project.helper import get_project_data_senders
from datawinners.project.models import Reminder, Project
from datawinners.scheduler.vumiclient import Client, Connection

import logging
logger = logging.getLogger("django")


def send_reminders():
    reminders_grouped_project_id = _get_reminders_grouped_by_project()

    for project_id, reminders in reminders_grouped_project_id.items():
        dbm = utils.get_database_manager_for_org(reminders[0].organization)
        project = dbm._load_document(project_id, Project)
        if not project.is_reminder_enabled():
            continue
        for reminder in reminders:
            if _should_send_reminder(reminder, project):
                _send_reminder_to_project_datasenders(dbm, reminder,project)



def _get_reminders_grouped_by_project():
    reminders = Reminder.objects.all()
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
    vumiclient = Client(None, None, connection=Connection("vumi", "vumi", base_url="http://10.253.50.2:7000"))
    datasenders = get_project_data_senders(dbm,project)
    for datasender in datasenders:
        vumiclient.send_sms(to_msisdn=datasender.get('mobile_number'),
                            from_msisdn=_get_from_tel_number(reminder)
                            , message=reminder.message)


def _get_from_tel_number(reminder):
    organization_settings = OrganizationSetting.objects.get(organization=reminder.organization)
    return organization_settings.sms_tel_number


