# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account
from mangrove.datastore.documents import SubmissionLogDocument


def load_sms_data():
    dbm = load_manager_for_default_test_account()
    for i in range(1, 200):
        sender = "1234567890"
        receiver = 12345
        dbm.save(SubmissionLogDocument(channel="sms", source=sender,
                                                                destination=receiver, form_code="ddd", values={"EID": "CID001", "Q1": "prabhu", "Q2": 20},
                                                                status=True, error_message=""))


def delete_sms_data():
    dbm = load_manager_for_default_test_account()
    rows = dbm.load_all_rows_in_view('mangrove_views/submissionlog', reduce=False)
    for document in [each.value for each in rows]:
        dbm.delete(document)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            print 'Deleting earlier submissions'
            delete_sms_data()
        except Exception as e:
            print e.message
        print "Storing multiple submissions....."
        try:
            load_sms_data()
        except Exception as e:
            print e.message
        print "Done."
