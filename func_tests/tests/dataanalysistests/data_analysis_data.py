# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from datetime import datetime

PROJECT_NAME = "project_name"
QUESTIONS = "questions"
HEADERS = "headers"
DATA_RECORDS = "data_records"
DAILY_DATE_RANGE = "daily_date_range"
MONTHLY_DATE_RANGE = "month_date_range"
CURRENT_MONTH = "current_month"
LAST_MONTH = "last_month"
YEAR_TO_DATE = "year_to_date"

today = datetime.today()
month = today.month - 1
str_month = str(today.month - 1)
year = today.year

if month < 10:
    str_month = "0" + str(month)

if not month:
    month = 12
    year = today.year - 1

last_month_date = "12." + str_month + "." + str(year)

current_month_date = "01." + today.strftime("%m.%Y")

today_date = today.strftime("%d.%m.%Y")

def get_year_to_date_data():
    last_month_data = [u'cli10 Zorro 43 %s O- Pneumonia,Memory loss 23.23452,-28.3456 --' % last_month_date,
                       u'cli11 Aàntra 91 %s O+ Dry cough,Neurological disorders -45.234,89.32345 --' % last_month_date,
                       u'cli12 ànnita 45 %s B+ Pneumonia,Dry cough,Neurological disorders -78.233,-28.3324 --' % last_month_date]

    current_month_data = [u'cli13 Dmanda 89 %s AB Pneumonia,Neurological disorders 40.2,69.3123 --' % current_month_date,
                          u'cli14 Vamand 56 %s O+ Rapid weight loss,Pneumonia,Neurological disorders 58.3452,115.3345 --' % current_month_date,
                          u'cli15 M!lo 45 %s AB Pneumonia,Rapid weight loss 19.672,92.33456 --' % current_month_date,
                          u'cli16 K!llo 28 %s O- Rapid weight loss,Neurological disorders 19.672,92.33456 --' % current_month_date,
                          u'cli17 Catty 98 %s O- Memory loss,Pneumonia,Neurological disorders 33.23452,-68.3456 --' % today_date,
                          u'cli18 àntra 58 %s O+ Rapid weight loss,Memory loss,Dry cough -45.234,169.32345 --' % today_date,
                          u'cli9 Tinnita 27 %s B+ Rapid weight loss,Pneumonia,Neurological disorders -78.233,-28.3324 --' % today_date]

    if today.month > 1:
        return last_month_data + current_month_data
    return current_month_data


DEFAULT_DATA_FOR_ANALYSIS = {PROJECT_NAME: "clinic test project",
                             HEADERS: [u'Clinic', u'Reporting Period', u'Submission Date', u'Data Sender',
                                       u'What is your namé?',
                                       u'What is age öf father?',
                                       u'What is your blood group?',
                                       u'What aré symptoms?',
                                       u'What is the GPS code for clinic?',
                                       u'What are the required medicines?'],
                             DATA_RECORDS: [
                                 u'Test cid001 25.12.2011 23.8.2012 Tester Pune Bob 89.0 O- Rapid weight loss, Pneumonia -18.1324 27.6547 Vid\xe9x EC',
                                 u'Test cid003 22.08.2012 22.08.2012 Shweta rep1 Mr. Tessy 77 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789 Hivid',
                                 u'Test cid003 22.08.2012 22.08.2012 Shweta rep1 Mr. Tessy 77 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789 Hivid',
                                 u'Andapa cli9 22.8.2012 22.08.2012 Shweta rep1 Tinnita 27 B+ Rapid weight loss, Pneumonia, Neurological disorders -78.233 -28.3324 --',
                                 u'Mahajanga cli18 22.8.2012 22.08.2012 Shweta rep1 \xe0ntra 58 O+ Rapid weight loss, Memory loss, Dry cough -45.234 169.32345 --',
                                 u'Sainte-Marie cli17 22.8.2012 22.08.2012 Shweta rep1 Catty 98 O- Memory loss, Pneumonia, Neurological disorders 33.23452 -68.3456 --',
                                 u'Andapa cli9 22.8.2012 22.08.2012 Shweta rep1 Tinnita 37 B+ Rapid weight loss, Pneumonia, Neurological disorders -78.233 -28.3324 --',
                                 u'Mahajanga cli18 22.8.2012 22.08.2012 Shweta rep1 \xe0ntra 28 O+ Rapid weight loss, Memory loss, Dry cough -45.234 169.32345 --',
                                 u'Sainte-Marie cli17 22.8.2012 22.08.2012 Shweta rep1 Catty 78 O- Memory loss, Pneumonia, Neurological disorders 33.23452 -68.3456 --',
                                 u'Fianarantsoa-I cli16 01.8.2012 02.08.2012 Shweta rep1 K!llo 28 O- Rapid weight loss, Neurological disorders 19.672 92.33456 --']
                             }


DEFAULT_DATA_FOR_QUESTIONNAIRE = {PROJECT_NAME: "clinic test project1",
                                  QUESTIONS: [u'What is your namé?',
                                              u'What is age öf father?',
                                              u'What is réporting date?',
                                              u'What is your blood group?',
                                              u'What aré symptoms?',
                                              u'What is the GPS code for clinic?',
                                              u'What are the required medicines?'],
                                  DATA_RECORDS: [
                                      u'cid001 Ianda (",) 34 27.03.2011 B+ Dry cough,Neurological disorders 38.3452,15.3345 --',
                                      u'cid002 Amanda 69 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 --',
                                      u'cid003 Jimanda 86 12.03.2011 AB Dry cough,Memory loss 40.2,69.3123 Hivid,Vidéx EC',
                                      u'cid004 Panda (",) 34 27.03.2011 B+ Dry cough,Neurological disorders 38.3452,15.3345 --',
                                      u'cid005 Vanda (",) 34 27.03.2011 B+ Dry cough,Neurological disorders 38.3452,15.3345 --',
                                      u'cid007 Amanda 73 12.11.2010 AB Dry cough,Memory loss 40.2,69.3123 --',
                                      u'cli10 Zorro 43 %s O- Pneumonia,Memory loss 23.23452,-28.3456 --' % last_month_date,
                                      u'cli11 Aàntra 91 %s O+ Dry cough,Neurological disorders -45.234,89.32345 --' % last_month_date,
                                      u'cli12 ànnita 45 %s B+ Pneumonia,Dry cough,Neurological disorders -78.233,-28.3324 --' % last_month_date,
                                      u'cli13 Dmanda 89 %s AB Pneumonia,Neurological disorders 40.2,69.3123 --' % current_month_date]}

FILTER_BY_CURRENT_MONTH = {PROJECT_NAME: "clinic test project",
                           DAILY_DATE_RANGE: CURRENT_MONTH,
                           DATA_RECORDS: [
                               u'cli13 Dmanda 89 %s AB Pneumonia,Neurological disorders 40.2,69.3123 --' % current_month_date,
                               u'cli14 Vamand 56 %s O+ Rapid weight loss,Pneumonia,Neurological disorders 58.3452,115.3345 --' % current_month_date,
                               u'cli15 M!lo 45 %s AB Pneumonia,Rapid weight loss 19.672,92.33456 --' % current_month_date,
                               u'cli16 K!llo 28 %s O- Rapid weight loss,Neurological disorders 19.672,92.33456 --' % current_month_date,
                               u'cli17 Catty 98 %s O- Memory loss,Pneumonia,Neurological disorders 33.23452,-68.3456 --' % today_date,
                               u'cli18 àntra 58 %s O+ Rapid weight loss,Memory loss,Dry cough -45.234,169.32345 --' % today_date,
                               u'cli9 Tinnita 27 %s B+ Rapid weight loss,Pneumonia,Neurological disorders -78.233,-28.3324 --' % today_date]}
FILTER_BY_LAST_MONTH = {PROJECT_NAME: "clinic test project",
                        DAILY_DATE_RANGE: LAST_MONTH,
                        DATA_RECORDS: [
                            u'cli10 Zorro 43 %s O- Pneumonia,Memory loss 23.23452,-28.3456 --' % last_month_date,
                            u'cli11 Aàntra 91 %s O+ Dry cough,Neurological disorders -45.234,89.32345 --' % last_month_date,
                            u'cli12 ànnita 45 %s B+ Pneumonia,Dry cough,Neurological disorders -78.233,-28.3324 --' % last_month_date,
                            u'cli9 Demelo 32 %s AB Dry cough,Rapid weight loss 19.672,92.33456 --' % last_month_date]}

FILTER_BY_YEAR_TO_DATE = {PROJECT_NAME: "clinic test project",
                          DAILY_DATE_RANGE: YEAR_TO_DATE,
                          DATA_RECORDS: get_year_to_date_data()}


