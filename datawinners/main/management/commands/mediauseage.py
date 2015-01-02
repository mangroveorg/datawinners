import datetime
import os
from django.core.management.base import BaseCommand
from datawinners.main.couchdb.utils import all_db_names
from datawinners.settings import EMAIL_HOST_USER, HNI_SUPPORT_EMAIL_ID
from django.core.mail import EmailMessage
from datawinners.project.media_usage.calculate_media_usage import calculate_usage


class Command(BaseCommand):
    def handle(self, *args, **options):
        log_folder = "/var/tmp/media_usage"
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        log_file_name = "%s" % datetime.datetime.now().strftime('media_usage_%H_%M_%d_%m_%Y.log')
        full_log_file_path = "%s/%s" % (log_folder, log_file_name)
        print "Calculate media usage per account"
        with open(full_log_file_path, "w") as log_file:
            for db_name in all_db_names():
                calculate_usage(db_name, log_file)
        self.send_email(full_log_file_path)
        print "Done."

    def send_email(self, log_file_path):
        email = EmailMessage(subject="Space usage for media files - %s" % datetime.datetime.today(),
                             from_email=EMAIL_HOST_USER, to=[HNI_SUPPORT_EMAIL_ID])
        email.attach_file(mimetype='text/plain', path=log_file_path)
        email.send()

