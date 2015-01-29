import datetime
import os
import re
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


def _calculate_total_usage(log_file_path):
    pattern = re.compile("^Total used: (\d+.\d+) mb")
    grand_total_usage = 0
    with open(log_file_path, 'r') as f:
        for line in f.readlines():
            match = pattern.match(line)
            if match:
                grand_total_usage += float(match.group(1))

    return grand_total_usage


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

        if os.path.exists(full_log_file_path):

            grand_tot_usage = _calculate_total_usage(full_log_file_path)
            with open(full_log_file_path, 'a') as f:
                f.write("\nTotal usage across accounts: %s mb\n" % grand_tot_usage)

            if 'send-mail' in args:
                    print "Sending mail..."
                    _send_email(full_log_file_path)
            print "Log file path: %s" % full_log_file_path
        else:
            print "No media usage across accounts."
        print "Done."

