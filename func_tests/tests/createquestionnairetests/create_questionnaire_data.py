# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
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

QUESTIONNAIRE_DATA = {QUESTIONNAIRE_CODE: "WPS", GEN_RANDOM: True,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "WID"},
                      QUESTIONS: [{QUESTION: "Water Level", CODE: "WL", TYPE: NUMBER, MIN: "1", MAX: "10"},
                              {QUESTION: "Date of report", CODE: "DR", TYPE: DATE, DATE_FORMAT: DD_MM_YYYY},
                              {QUESTION: "Color of Water", CODE: "WC", TYPE: LIST_OF_CHOICES,
                               CHOICE: ["LIGHT RED", "LIGHT YELLOW", "DARK YELLOW"],
                               ALLOWED_CHOICE: ONLY_ONE_ANSWER},
                              {QUESTION: "Water point admin name", CODE: "WAN", TYPE: WORD, LIMIT: LIMITED, MAX: "10"},
                              {QUESTION: "Bacterias in water", CODE: "WB", TYPE: LIST_OF_CHOICES,
                               CHOICE: ["Aquificae", "Bacteroids", "Chlorobia"],
                               ALLOWED_CHOICE: MULTIPLE_ANSWERS},
                              {QUESTION: "Geo points of water point", CODE: "GPS", TYPE: GEO}],
                      CHARACTER_REMAINING: "65 / 160 characters used",
                      SUCCESS_MSG: "Your questionnaire has been saved",
                      PAGE_TITLE: "Data Senders"}
