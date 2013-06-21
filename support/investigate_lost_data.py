from collections import defaultdict
import pprint
import itertools
import cPickle
import datetime
import os
import re
from datawinners.accountmanagement.models import OrganizationSetting
from mangrove.datastore.database import get_db_manager

IN_COMMING_PATTERN = r"^(.+)\+0000.+INCOMING.+<<<<(.+short_message.+)$"

SUCCESS_OUTGOING_PATTERN = r"^(.+)\+0000.+OUTGOING.+>>>>(.+short_message.+'(Thank|Misaotra).+)$"

DATA_SENDER_NOT_FOUND_PATTERN = "^(.+)\+0000.+OUTGOING.+>>>>(.+short_message.+Your telephone number is not yet registered in our system. Please contact your supervisor..+)$"

VUMI_LOG_FOLDER = "/Users/twer/prod-vumi-log/logs"

SMS_ORG_DICT = {org_setting.sms_tel_number:org_setting.document_store for org_setting in OrganizationSetting.objects.all()}

class Message(object):
    def __init__(self, source, destination, short_message, submit_date=None):
        self._source = source
        self._destination = destination
        self._short_message = short_message
        self._submit_date = submit_date

    @staticmethod
    def from_string(submit_date, message):
        message_dict = eval(message)
        params = message_dict.get("body").get("mandatory_parameters")
        return Message(params.get("source_addr"), params.get("destination_addr"), params.get("short_message"), submit_date)

    @property
    def source(self):
        return self._source

    @property
    def destination(self):
        return self._destination

    @property
    def submit_date(self):
        return datetime.datetime.strptime(self._submit_date, '%Y-%m-%d %H:%M:%S')

    @property
    def message(self):
        return self._short_message

    def is_same_conversation(self, other):
        assert isinstance(other, Message)
        return (self.source, self.destination) == (other.destination, other.source)

    def get_form_code(self):
        return self.message.strip().split(' ')[0]

    def __repr__(self):
        return "Submit Date: %s, Sender: %s, Receiver: %s, Data: %s" % (self.submit_date, self.source, self.destination, self._short_message)

    def __eq__(self, other):
        assert isinstance(other, Message)
        if other == self:
            return True
        return self.source, self.destination, self.message == other.source, other.destination, other.message

def extract_submission(f):
    for line in f.readlines():
        outgoing = re.findall(SUCCESS_OUTGOING_PATTERN, line)
        incomming = re.findall(IN_COMMING_PATTERN, line)
        data_sender_not_found = re.findall(DATA_SENDER_NOT_FOUND_PATTERN, line)
        if incomming:
            incomming_msg =(Message.from_string(incomming[0][0], incomming[0][1]))
            submissions.append(incomming_msg)
        elif outgoing:
            outgoing_msg = Message.from_string(outgoing[0][0], outgoing[0][1])
            success_outgoing.append(outgoing_msg)
            if outgoing_msg.is_same_conversation(incomming_msg):
                success_incoming.append(incomming_msg)
                print ">>"*80
                print "Found one conversation:"
                print incomming_msg
                print outgoing_msg
        elif data_sender_not_found:
            lost_data_senders.append(Message.from_string(data_sender_not_found[0][0], data_sender_not_found[0][1]))

def scan_log(log):
    log_file = os.path.join(VUMI_LOG_FOLDER, log)
    print "Log file: ", log
    print "="*80
    with open(log_file) as f:
        extract_submission(f)

def main():
    airtel_2_logs = ["smpp_transport_airtel_mad_2_1.log.2",
             "smpp_transport_airtel_mad_2_1.log.1",
             "smpp_transport_airtel_mad_2_1.log"]
    airtel_1_logs = ["smpp_transport_airtel_mad_1_1.log.2",
             "smpp_transport_airtel_mad_1_1.log.1",
             "smpp_transport_airtel_mad_1_1.log"]
    clickatell_logs = ["smpp_transport_clickatell_1.log"]
    infobip_logs = ["smpp_transport_infobip_1.log.1",
             "smpp_transport_infobip_1.log"]
    smsgh_logs = ["smpp_transport_smsgh_1.log.1",
             "smpp_transport_smsgh_1.log"]
    for log in itertools.chain(airtel_1_logs, airtel_2_logs, clickatell_logs, infobip_logs, smsgh_logs):
        try:
            scan_log(log)
        except Exception:
            pass

lost_data_senders = []
submissions = []
success_incoming = []
success_outgoing = []
incomming_msg = None
server = "http://localhost:5984"

if __name__ == '__main__':
    main()

    pprint.pprint(submissions)
    print "All success outgoing"
    pprint.pprint(success_outgoing)
    print "All success incoming"
    pprint.pprint(success_incoming)

    print "Size of submissions: ", len(submissions)
    print "Size of success outgoing: ", len(success_outgoing)
    print "Size of success incoming: ", len(success_incoming)


    org_set = set()
    for submission in success_incoming:
        org_set.add(SMS_ORG_DICT.get(submission.destination, None))

    success_submissions_by_org = defaultdict(list)
    for sms_tel_number, document_store in SMS_ORG_DICT.items():
        if sms_tel_number is None: continue
        submissions = success_submissions_by_org[document_store]
        submissions.extend([submission for submission in success_incoming if sms_tel_number.find(submission.destination) != -1])

        if submissions:
            print '='*80
            print
            print document_store
            print "Size of success submission in %s is %d" % (document_store, len(submissions))
            submissions = sorted(submissions, key=lambda s: s.submit_date)
            groups = []
            uniquekeys = []
            for k, g in itertools.groupby(submissions, key=lambda s: s.get_form_code()):
                groups.append(list(g))
                uniquekeys.append(k)
            print uniquekeys
            pprint.pprint(groups)

    print
    print "Submissions are under", org_set
