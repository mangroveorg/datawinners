# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from apscheduler.scheduler import Scheduler
from django.conf import settings
from django.core.management.base import BaseCommand
from datawinners.deactivate.deactive import send_deactivate_email, deactivate_expired_trial_account
from datawinners.scheduler.scheduler import send_reminders, send_time_based_reminder_email
from datawinners.main.couchdb.view_updater import update_all_views

import logging

logger = logging.getLogger("django")

class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = Scheduler(daemonic=False)
        logger.info("started the scheduler")
        scheduler.add_cron_job(send_reminders, hour=settings.SCHEDULER_HOUR, minute=settings.SCHEDULER_MINUTES)
        scheduler.add_cron_job(send_time_based_reminder_email, hour=settings.SCHEDULER_HOUR, minute=settings.SCHEDULER_MINUTES)
        scheduler.add_cron_job(deactivate_expired_trial_account, hour=settings.SCHEDULER_HOUR, minute=settings.SCHEDULER_MINUTES)
        scheduler.add_cron_job(update_all_views, hour=settings.SCHEDULER_HOUR, minute=settings.SCHEDULER_MINUTES)
        scheduler.start()
