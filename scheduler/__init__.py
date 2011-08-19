from _collections import defaultdict
from apscheduler.scheduler import Scheduler
from datawinners import utils
from datawinners.project.models import Reminder
from datawinners.project.models import Project

from datetime import date
from mangrove.datastore import database


sched = Scheduler()
sched.start()



def send_reminders():
    reminders = Reminder.objects.filter(days_before = date.today().day)
    reminders_grouped_project_id = defaultdict(list)
    for reminder in reminders:
        reminders_grouped_project_id[reminder.project_id].append(reminder)

    for project_id, reminder in reminders_grouped_project_id.items():
        dbm = utils.get_database_manager_for_org(reminder.organization)
        

