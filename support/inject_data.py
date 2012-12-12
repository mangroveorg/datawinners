import commands
from datetime import datetime
from email.mime.text import MIMEText
from sys import stdout
import os
import smtplib
from time import sleep
import urllib2
import jsonpickle

DB_NAME = "stability_test"

doc='''{
    "status": true,
    "document_type": "SubmissionLog",
    "destination": "1902",
    "event_time": "2012-11-16T15:03:38.357206+00:00",
    "created": "2012-12-08T15:03:38.357206+00:00",
    "error_message": "",
    "modified": "2012-11-16T15:03:38.527112+00:00",
    "form_code": "ntd",
    "source": "100000",
    "values": {
        "q1": "sch104",
        "q2": "11.2012",
        "q3": "450",
        "q4": "385",
        "q5": "448",
        "q6": "384",
        "q7": "25",
        "q8": "30",
        "q9": "200",
        "q10": "52"
    },
    "test": true,
    "data_record_id": "cd2974b42ffe11e2b4b4fefdb24fb922",
    "submitted_on": "2012-11-16T15:03:38.357238+00:00",
    "void": false,
    "channel": "script"
}'''

def _get_doc_count():
    summary = urllib2.urlopen("http://localhost:5984/%s" % DB_NAME).read()
    print summary
    return jsonpickle.decode(summary).get('doc_count', 0)

def send_mail(doc_count_before, doc_count_after):
    msg = MIMEText("Got it! %s before:%s after:%s" % (str(datetime.now()), doc_count_before, doc_count_after))
    msg['Subject'] = 'Couchbase down, couchbase down.'
    msg['From'] = "iamnobody250@gmail.com"
    msg['To'] = "edfeng@thoughtworks.com;qszhuan@thoughtworks.com"
    s = smtplib.SMTP()
    s.connect('smtp.gmail.com:587')
    s.ehlo()
    s.starttls()
    s.esmtp_features['auth'] = 'LOGIN DIGEST-MD5 PLAIN'
    s.login("iamnobody250@gmail.com", "123!@#qQ")
    s.sendmail("iamnobody250@gmail.com", ["edfeng@thoughtworks.com", "qszhuan@thoughtworks.com"], msg.as_string())
    s.quit()

def verify():
    doc_count_before = _get_doc_count()
    print str(datetime.utcnow()) + 'doc count before restart: %d' % doc_count_before
    print os.system("/etc/init.d/couchbase-server restart")
    sleep(10)
    doc_count_after = _get_doc_count()
    print str(datetime.utcnow()) + 'doc count after restart: %d' % doc_count_after

    if doc_count_before != doc_count_after:
        send_mail(doc_count_before, doc_count_after)



def run(db_name):
    print str(datetime.utcnow()) + 'inject data:'
    for i in range(500):
        stdout.write(".")
        stdout.flush()
        commands.getoutput('''curl -i -d '%s' -X POST -H "Content-Type: application/json" http://localhost:5984/%s/_bulk_docs ''' % (data, db_name))
    print str(datetime.utcnow()) + 'inject over.'
def go():
    while True:
        run(DB_NAME)
        verify()
        sleep(30)

data = '{"docs":[%s]}' % ','.join([doc]*100)
commands.getoutput("curl -X PUT http://localhost:5984/%s" % DB_NAME)

go()
