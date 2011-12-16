import datetime
from django.core.management.base import BaseCommand
from datawinners.scheduler.scheduler import send_reminders

class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Sending reminders scheduled for %s" % datetime.datetime.now()
        send_reminders()
        print "Done."
