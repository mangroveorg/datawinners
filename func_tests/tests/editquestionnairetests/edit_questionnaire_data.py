# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
PROJECT_NAME = "project_name"
PAGE_TITLE = "page_title"
QUESTIONNAIRE_CODE = "questionnaire_code"
GEN_RANDOM = "gen_random"
DEFAULT_QUESTION = "default_question"
QUESTION = "question"
QUESTIONS = "questions"
CODE = "code"
TYPE = "type"
LIMIT = "limit"
NO_LIMIT = "no_limit"
LIMITED = "limited"
MIN = "min"
MAX = "max"
DATE_FORMAT = "date_format"
CHOICE = "choice"
ALLOWED_CHOICE = "allowed_choice"
NUMBER = "number"
WORD = "word"
DATE = "date"
LIST_OF_CHOICES = "list_of_choices"
GEO = "geo"
DD_MM_YYYY = "dd.mm.yyyy"
MM_DD_YYYY = "mm.dd.yyyy"
MM_YYYY = "mm.yyyy"
ONLY_ONE_ANSWER = "only_one_answer"
MULTIPLE_ANSWERS = "multiple_answers"
ERROR_MSG = "message"
SUCCESS_MSG = "message"
CHARACTER_REMAINING = "character_remaining"

VALID_PROJECT_DATA = {PROJECT_NAME: "clinic5 test project"}

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: u"cli005",
                      DEFAULT_QUESTION: {QUESTION: u"What is associatéd entity?", CODE: u"EID"},
                      QUESTIONS: [{QUESTION: u"What is your namé?", CODE: u"NA", TYPE: WORD, LIMIT: LIMITED, MAX: u"10"},
                              {QUESTION: u"What is age öf father?", CODE: u"FA", TYPE: NUMBER, MIN: u"18", MAX: u"100"},
                              {QUESTION: u"What is réporting date?", CODE: u"RD", TYPE: DATE, DATE_FORMAT: DD_MM_YYYY},
                              {QUESTION: u"What is your blood group?", CODE: u"BG", TYPE: LIST_OF_CHOICES,
                               CHOICE: [u"O+", u"O-", u"AB", u"B+"],
                               ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                              {QUESTION: u"What aré symptoms?", CODE: u"SY", TYPE: LIST_OF_CHOICES,
                               CHOICE: [u"Rapid weight loss", u"Dry cough", u"Pneumonia", u"Memory loss",
                                        u"Neurological disorders "],
                               ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                              {QUESTION: u"What is the GPS codé for clinic", CODE: u"GPS", TYPE: GEO}],
                      CHARACTER_REMAINING: u"84 / 160 characters used"}
