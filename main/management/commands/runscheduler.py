# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from apscheduler.scheduler import Scheduler
from django.core.management.base import BaseCommand
from datawinners.scheduler.scheduler import send_reminders

import logging
from datawinners.settings import SCHEDULER_HOUR, SCHEDULER_MINUTES

logger = logging.getLogger("django")

class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = Scheduler(daemonic=False)
        logger.info("started the scheduler")
        scheduler.add_cron_job(send_reminders,  hour=SCHEDULER_HOUR,minute=SCHEDULER_MINUTES)
        scheduler.start()


