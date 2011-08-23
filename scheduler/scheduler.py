# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from _collections import defaultdict
from datetime import date
from apscheduler.scheduler import Scheduler
from datawinners import utils
from datawinners.accountmanagement.models import OrganizationSetting
from datawinners.entity.import_data import load_all_subjects_of_type
from datawinners.project.models import Reminder, Project
from datawinners.scheduler.vumiclient import Client, Connection

import logging
logger = logging.getLogger("django")

def _get_reminders_grouped_by_project():
    reminders = Reminder.objects.filter(day_of_the_month=date.today().day)
    reminders_grouped_project_id = defaultdict(list)
    for reminder in reminders:
        reminders_grouped_project_id[reminder.project_id].append(reminder)
    return reminders_grouped_project_id


def _is_reminder_enabled_for_project(project):
    return project.reminders


def _should_send_reminder(reminder):
    return reminder.day_of_the_month == date.today().day


def _send_reminder_to_datasenders(dbm, reminder):
    vumiclient = Client(None, None, connection=Connection("vumi", "vumi", base_url="http://10.253.50.2:7000"))
    #TODO get the datasender attached to the project
    datasenders = load_all_subjects_of_type(dbm)
    organization_settings = OrganizationSetting.objects.get(organization=reminder.organization)
    for datasender in datasenders:
        vumiclient.send_sms(to_msisdn=datasender.get('mobile_number'),
                            from_msisdn=organization_settings.sms_tel_number
                            , message=reminder.message)


def send_reminders():
    reminders_grouped_project_id = _get_reminders_grouped_by_project()

    for project_id, reminders in reminders_grouped_project_id.items():
        dbm = utils.get_database_manager_for_org(reminders[0].organization)
        project = dbm._load_document(project_id, Project)
        if not _is_reminder_enabled_for_project(project):
            continue
        for reminder in reminders:
            if _should_send_reminder(reminder):
                _send_reminder_to_datasenders(dbm, reminder)

