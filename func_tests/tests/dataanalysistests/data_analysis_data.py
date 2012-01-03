# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime

PROJECT_NAME = "project_name"
QUESTIONS = "questions"
DATA_RECORDS = "data_records"
DATE_RANGE = "date_range"
CURRENT_MONTH = "current_month"
LAST_MONTH = "last_month"
YEAR_TO_DATE = "year_to_date"

today = datetime.today()
month = today.month - 1
year = today.year
if not(month):
    month = 12
    year = today.year - 1
last_month_date = "12." + str(month) + "." + str(year)

current_month_date = "01." + str(today.month) + "." + str(today.year)

today_date = str(today.day) + "." + str(today.month) + "." + str(today.year)

def get_year_to_date_data():
    march_data = [
        u'cid001 ànita 45 07.03.2011 O- Dry cough,Neurological disorders 45.233,28.3324 --',
        u'cid002 Amanda 69 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 --',
        u'cid003 Jimanda 86 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 --',
        u'cid004 ànnita 30 07.03.2011 O- Dry cough,Neurological disorders 45.233,28.3324 --',
        u'cid005 Qamanda 47 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 --',]

    last_month_data  =  [u'cli10 Zorro 43 %s O- Pneumonia,Memory loss 23.23452,-28.3456 --' % last_month_date,
                         u'cli11 Aàntra 91 %s O+ Dry cough,Neurological disorders -45.234,89.32345 --' % last_month_date,
                         u'cli12 ànnita 45 %s B+ Pneumonia,Dry cough,Neurological disorders -78.233,-28.3324 --' % last_month_date,]

    current_month_data =[u'cli13 Dmanda 89 %s AB Pneumonia,Neurological disorders 40.2,69.3123 --' % current_month_date,
                         u'cli14 Vamand 56 %s O+ Rapid weight loss,Pneumonia,Neurological disorders 58.3452,115.3345 --' % current_month_date,
                         u'cli15 M!lo 45 %s AB Pneumonia,Rapid weight loss 19.672,92.33456 --' % current_month_date,
                         u'cli16 K!llo 28 %s O- Rapid weight loss,Neurological disorders 19.672,92.33456 --' % current_month_date,
                         u'cli17 Catty 98 %s O- Memory loss,Pneumonia,Neurological disorders 33.23452,-68.3456 --' % today_date,
                         u'cli18 àntra 58 %s O+ Rapid weight loss,Memory loss,Dry cough -45.234,169.32345 --' % today_date,
                         u'cli9 Tinnita 27 %s B+ Rapid weight loss,Pneumonia,Neurological disorders -78.233,-28.3324 --' % today_date]

    if today.month > 1:
        return last_month_data + current_month_data
    return current_month_data

DEFAULT_DATA_FOR_QUESTIONNAIRE = {PROJECT_NAME: "clinic test project",
                      QUESTIONS: [u'What is your namé?',
                                  u'What is age öf father?',
                                  u'What is réporting date?',
                                  u'What is your blood group?',
                                  u'What aré symptoms?',
                                  u'What is the GPS codé for clinic',
                                  u'What are the required medicines?'],
                      DATA_RECORDS: [u'cid001 ànita 45 07.03.2011 O- Dry cough,Neurological disorders 45.233,28.3324 --',
                                     u'cid002 Amanda 69 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 --',
                                     u'cid003 Jimanda 86 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 --',
                                     u'cid004 ànnita 30 07.03.2011 O- Dry cough,Neurological disorders 45.233,28.3324 --',
                                     u'cid005 Qamanda 47 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 --',
                                     u'cid007 Amanda 73 12.11.2010 AB Dry cough,Memory loss 40.2,69.3123 --',
                                     u'cli10 Zorro 43 %s O- Pneumonia,Memory loss 23.23452,-28.3456 --' % last_month_date,
                                     u'cli11 Aàntra 91 %s O+ Dry cough,Neurological disorders -45.234,89.32345 --' % last_month_date,
                                     u'cli12 ànnita 45 %s B+ Pneumonia,Dry cough,Neurological disorders -78.233,-28.3324 --' % last_month_date,
                                     u'cli13 Dmanda 89 %s AB Pneumonia,Neurological disorders 40.2,69.3123 --' % current_month_date]}

FILTER_BY_CURRENT_MONTH = {PROJECT_NAME: "clinic test project",
                           DATE_RANGE: CURRENT_MONTH,
                           DATA_RECORDS: [u'cli13 Dmanda 89 %s AB Pneumonia,Neurological disorders 40.2,69.3123 --' % current_month_date,
                                    u'cli14 Vamand 56 %s O+ Rapid weight loss,Pneumonia,Neurological disorders 58.3452,115.3345 --' % current_month_date,
                                    u'cli15 M!lo 45 %s AB Pneumonia,Rapid weight loss 19.672,92.33456 --' % current_month_date,
                                    u'cli16 K!llo 28 %s O- Rapid weight loss,Neurological disorders 19.672,92.33456 --' % current_month_date,
                                    u'cli17 Catty 98 %s O- Memory loss,Pneumonia,Neurological disorders 33.23452,-68.3456 --' % today_date,
                                    u'cli18 àntra 58 %s O+ Rapid weight loss,Memory loss,Dry cough -45.234,169.32345 --' % today_date,
                                    u'cli9 Tinnita 27 %s B+ Rapid weight loss,Pneumonia,Neurological disorders -78.233,-28.3324 --' % today_date]}

FILTER_BY_LAST_MONTH = {PROJECT_NAME: "clinic test project",
                           DATE_RANGE: LAST_MONTH,
                           DATA_RECORDS: [u'cli10 Zorro 43 %s O- Pneumonia,Memory loss 23.23452,-28.3456 --' % last_month_date,
                                    u'cli11 Aàntra 91 %s O+ Dry cough,Neurological disorders -45.234,89.32345 --' % last_month_date,
                                    u'cli12 ànnita 45 %s B+ Pneumonia,Dry cough,Neurological disorders -78.233,-28.3324 --' % last_month_date,
                                    u'cli9 Demelo 32 %s AB Dry cough,Rapid weight loss 19.672,92.33456 --' % last_month_date]}

FILTER_BY_YEAR_TO_DATE = {PROJECT_NAME: "clinic test project",
                          DATE_RANGE: YEAR_TO_DATE,
                          DATA_RECORDS: get_year_to_date_data()}

