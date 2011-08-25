# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from apscheduler.scheduler import Scheduler
from django.core.management.base import BaseCommand
from datawinners.scheduler.scheduler import send_reminders

import logging
logger = logging.getLogger("django")

class Command(BaseCommand):
    def handle(self, *args, **options):
        sched = Scheduler(daemonic=False)
        sched.add_cron_job(send_reminders, hours=10)
        sched.start()

