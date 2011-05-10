# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from mangrove.datastore.database import get_db_manager
from datawinners.main.management.commands.recreateviews import create_views
from mangrove.transport.submissions import SubmissionHandler, Request


def load_sms_data():
    s = SubmissionHandler(dbm=get_db_manager())
    for i in range(1,20):
        message = "QRID01 +EID CID001 +Q1 prabhu +Q2 20"
        sender = "1234567890"
        receiver = 12345
        response = s.accept(Request(transport="sms", message=message, source=sender, destination=receiver))
        message = "QRID01 +EID CID002 +Q1 shweta +Q2 30"
        response = s.accept(Request(transport="sms", message=message, source=sender, destination=receiver))
        message = "QRID01 +EID CID003 +Q1 prabhu +Q2 20"
        response = s.accept(Request(transport="sms", message=message, source=sender, destination=receiver))


class Command(BaseCommand):
    def handle(self, *args, **options):
        manager = get_db_manager()
        print "Storing multiple submissions....."
        try:
            load_sms_data()
        except:
            print "Exception!!!"
        print "Done."