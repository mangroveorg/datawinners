# coding=utf-8
PROJECT_NAME = "project_name"
PAGE_TITLE = "page_title"
QUESTIONNAIRE_CODE = "questionnaire_code"
GEN_RANDOM = "gen_random"
DEFAULT_QUESTION = "default_question"
QUESTION = "question"
QUESTIONS = "questions"
CODE = "code"
TYPE = "type"
NUMBER = "number"
WORD = "word"
LIMIT = "limit"
NO_LIMIT = "no_limit"
LIMITED = "limited"
MIN = "min"
MAX = "max"

PROJECT_DATA = {
                      PROJECT_NAME: "ft-project sms reply", GEN_RANDOM: True,
                    }

PROJECT_QUESTIONNAIRE_DATA = {
                      QUESTIONNAIRE_CODE: None, GEN_RANDOM: False,
                      QUESTIONS: [
                          {QUESTION: u"What is your namé?", CODE: u"q3", TYPE: WORD, LIMIT: LIMITED, MAX: u"10"},
                          {QUESTION: u"What is age öf father?", CODE: u"q4", TYPE: NUMBER, MIN: u"18", MAX: u"100"},
                      ],
                      PAGE_TITLE: "Data Senders"
                     }