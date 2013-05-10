from datetime import datetime
import glob
from pprint import pprint
from xlrd import open_workbook
from mangrove.datastore.database import get_db_manager
from mangrove.transport import TransportInfo, Request
from mangrove.transport.player.player import SMSPlayer
from mangrove.transport.contract.submission import Submission

#submission date,       source,     destination, messages,
#2012-11-24 13:48:22	24535435348	26134535750	 009 MCHTDV07 22.11.2012 ABE0000369 72.15 0 0 0 0
import settings

data_folder = "/Users/twer/Downloads/lost_data_folder/*.xlsx"

db_server = "localhost"
db_name = "hni_crs-stock_jhw14178"
db_credentials = settings.COUCHDBMAIN_CREDENTIALS

dbm = get_db_manager(server="http://%s:5984" % db_server, database=db_name,credentials=db_credentials)
sms_player = SMSPlayer(dbm)

def update_submission_date(response, submission_date):
    submission = Submission.get(dbm, response.submission_id)
    submission._doc.submitted_on = submission_date
    submission._doc.created = submission_date
    submission._doc.event_time = submission_date
    submission.save()
    pprint(submission.values)

def send_sms(source, destination, text):
    print text
    transport_info = TransportInfo(transport="sms", source=source, destination=destination)
    response = sms_player.accept(Request(message=text, transportInfo=transport_info))
    print response
    return response

for xls in glob.glob(data_folder):
    workbook = open_workbook(xls)
    sheets_ = workbook.sheets()[0]

    for row_num in range(sheets_.nrows):
        row = sheets_.row_values(row_num)
        submission_date, source, dest, values = tuple(row)
        source, dest = str(int(source)), str(int(dest))
        print values
        response = send_sms(source, dest, values)

        submission_date = datetime.strptime(submission_date, "%Y-%m-%d %H:%M:%S")
        update_submission_date(response, submission_date)
