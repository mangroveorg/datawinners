from datetime import datetime
import glob
from pprint import pprint
from xlrd import open_workbook
from mangrove.datastore.database import get_db_manager
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport import TransportInfo
from mangrove.transport.submissions import Submission

#submission date,       source,     destination, messages,
#2012-11-24 13:48:22	24535435348	26134535750	 009 MCHTDV07 22.11.2012 ABE0000369 72.15 0 0 0 0
data_folder = "/Users/twer/Downloads/DataLost/*.xls"

db_server = ""
db_name = ""

dbm = get_db_manager(server="http://%s:5984" % db_server, database=db_name)

def insert_submission(source, dest, form_model, value_dict, submission_date):
    submission = Submission(dbm=dbm, transport_info=TransportInfo('sms', source, dest), form_code=form_model.form_code,
        values=value_dict)
    submission._doc.submitted_on = submission_date
    submission._doc.created = submission_date
    submission.update(True, '', is_test_mode=form_model.is_in_test_mode())
    pprint(submission.values)


for xls in glob.glob(data_folder):
    workbook = open_workbook(xls)
    sheets_ = workbook.sheets()[0]
    for row_num in range(sheets_.nrows):
        row = sheets_.row_values(row_num)
        submission_date, source, dest, values, _ = tuple(row)
        submission_date = datetime.strptime(submission_date, "%Y-%m-%d %H:%M:%S")
        source, dest = str(int(source)), str(int(dest))
        value_list = values.split()
        form_code, answers = value_list[0].lower(), value_list[1:]
        form_model = get_form_model_by_code(dbm, form_code)
        field_codes = map(lambda x: x.code, form_model.fields)
        d = dict(zip(field_codes, answers))

        insert_submission(source, dest, form_model, d, submission_date)
