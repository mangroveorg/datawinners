# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

PROJECT_NAME = "project_name"
QCODE = 'qcode'
ANSWER = 'answer'
TYPE = "type"

SELECT = "select"
TEXT = "text"
CHECKBOX = "checkbox"

VALID_ANSWERS = [
    {QCODE: 'EID', ANSWER: 'Indore Clinic', TYPE: SELECT},
    {QCODE: 'NA', ANSWER: 'Bob', TYPE: TEXT},
    {QCODE: 'FA', ANSWER: '89', TYPE: TEXT},
    {QCODE: 'RD', ANSWER: '25.12.2011', TYPE: TEXT},
    {QCODE: 'BG', ANSWER: 'O-', TYPE: SELECT},
    {QCODE: 'SY', ANSWER: ['a', 'c'], TYPE: CHECKBOX},
    {QCODE: 'GPS', ANSWER: '-18.1324 27.6547', TYPE: TEXT},
    {QCODE: 'RM', ANSWER: ['c'], TYPE: CHECKBOX},
]

DEFAULT_ORG_DATA = {
    PROJECT_NAME: 'clinic test project'
}

TRIAL_ORG_DATA = {
    PROJECT_NAME: 'FILL ME IN!'
}
