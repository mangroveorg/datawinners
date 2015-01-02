import datetime
import os
from django.core.management.base import BaseCommand
from datawinners.main.couchdb.utils import all_db_names
from datawinners.settings import EMAIL_HOST_USER, HNI_SUPPORT_EMAIL_ID
from django.core.mail import EmailMessage
from datawinners.project.media_usage.calculate_media_usage import calculate_usage
from migration.couch.utils import DWThreadPool


def _send_email(log_file_path):
    email = EmailMessage(subject="Space usage for media files - %s" % datetime.datetime.today(),
                         from_email=EMAIL_HOST_USER, to=[HNI_SUPPORT_EMAIL_ID])
    email.attach_file(mimetype='text/plain', path=log_file_path)
    email.send()


class Command(BaseCommand):
    def handle(self, *args, **options):
        log_folder = "/var/tmp/media_usage"
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        log_file_name = "%s" % datetime.datetime.now().strftime('media_usage_%H_%M_%d_%m_%Y.log')
        full_log_file_path = "%s/%s" % (log_folder, log_file_name)
        print "Calculate media usage per account"
        pool = DWThreadPool(3, 3)
        for db_name in all_db_names():
            pool.submit(calculate_usage, db_name, full_log_file_path)
        pool.wait_for_completion()
        if 'send-mail' in args:
            if os.path.exists(full_log_file_path):
                print "Sending mail..."
                _send_email(full_log_file_path)
        print "Done."

