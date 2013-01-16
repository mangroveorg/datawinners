from xlrd import open_workbook
from scheduler.smsclient import SMSClient

filename = "/Users/twer/Downloads/SchoolsSMSGhana.xlsx"
workbook = open_workbook(filename)
organization_number = "1902"
area_code = "233"
sheets_ = workbook.sheets()[0]

sms_client = SMSClient()

print 'Start'
for row_num in range(1, sheets_.nrows):
    row = sheets_.row_values(row_num)
    _, _, data_sender_phone_number, message = tuple(row)
    phone_number = area_code + str(int(data_sender_phone_number))[1:]
    print ("Sending broadcast message to %s from %s.") % (phone_number, organization_number)

    sms_sent = sms_client.send_sms(organization_number, phone_number, message)
    print 'Response:', sms_sent
print 'End'
