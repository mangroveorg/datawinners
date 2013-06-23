# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.core.management.base import BaseCommand
from datawinners.main.initial_couch_fixtures import load_manager_for_default_test_account
from mangrove.datastore.documents import  SurveyResponseDocument


def load_sms_data():
    dbm = load_manager_for_default_test_account()
    for i in range(1, 200):
        sender = "1234567890"
        receiver = 12345
        dbm._save_document(SurveyResponseDocument(channel="sms",
                                                 destination=receiver, form_code="cli001",
                                                 values={"EID": "CID001", "Q1": "prabhu", "Q2": 20},
                                                 status=True, error_message=""))


def delete_sms_data():
    dbm = load_manager_for_default_test_account()
    rows = dbm.load_all_rows_in_view('mangrove_views/survey_response', reduce=False)
    for document in [each.value for each in rows]:
        dbm.delete(document)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            print 'Deleting earlier survey response'
            delete_sms_data()
        except Exception as e:
            print e.message
        print "Storing multiple survey response....."
        try:
            load_sms_data()
        except Exception as e:
            print e.message
        print "Done."
