import commands
from datetime import datetime
from email.mime.text import MIMEText
from sys import stdout
import os
import smtplib
from time import sleep
import urllib2
import jsonpickle

DB_NAME = "hni_crs-stock_jhw14178"

doc='''{
    "status": true,
    "document_type": "SubmissionLog",
    "destination": "1902",
    "event_time": "2012-11-16T15:03:38.357206+00:00",
    "created": "2012-12-08T15:03:38.357206+00:00",
    "error_message": "",
    "modified": "2012-11-16T15:03:38.527112+00:00",
    "form_code": "cli001",
    "source": "0000000000",
    "values": {
       "eid": "cli12",
       "na": "annita",
       "fa": "90",
       "rd": "07.11.2010",
       "bg": "b",
       "sy": "bbe",
       "gps": "45.233 28.3324",
       "EID": "cli12"
    },
    "test": true,
    "data_record_id": "cd2974b42ffe11e2b4b4fefdb24fb922",
    "submitted_on": "2012-11-16T15:03:38.357238+00:00",
    "void": true,
    "channel": "sms"
}'''

def _get_doc_count():
    summary = urllib2.urlopen("http://localhost:5984/%s" % DB_NAME).read()
    print summary
    return jsonpickle.decode(summary).get('doc_count', 0)

def send_mail(doc_count_before, doc_count_after):
    msg = MIMEText("Got it! %s before:%s after:%s" % (str(datetime.now()), doc_count_before, doc_count_after))
    msg['Subject'] = 'Couchdb is down, couchdb down.'
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
    print os.system("/etc/init.d/couchdbmain restart")
    sleep(10)
    doc_count_after = _get_doc_count()
    print str(datetime.utcnow()) + 'doc count after restart: %d' % doc_count_after

    if doc_count_before != doc_count_after:
        send_mail(doc_count_before, doc_count_after)



def run(db_name):
    print str(datetime.utcnow()) + 'inject data:'
    for i in range(10):
        stdout.write(".")
        stdout.flush()
        commands.getoutput('''curl -i -d '%s' -X POST -H "Content-Type: application/json" http://localhost:5984/%s/_bulk_docs ''' % (data, db_name))
    print str(datetime.utcnow()) + 'inject over.'
def go():
    while True:
        run(DB_NAME)
#        verify()
        exit()
        sleep(30)

data = '{"docs":[%s]}' % ','.join([doc]*100)
commands.getoutput("curl -X PUT http://localhost:5984/%s" % DB_NAME)

go()

