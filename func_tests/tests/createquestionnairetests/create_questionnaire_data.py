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
                      CHARACTER_REMAINING: "73 / 160 characters used (1 SMS)",
                      SUCCESS_MSG: "Your questionnaire has been saved",
                      PAGE_TITLE: "Data Senders"}

QUESTIONNAIRE_DATA1 = {QUESTIONNAIRE_CODE: "WPS", GEN_RANDOM: True,
                      DEFAULT_QUESTION: {QUESTION: "What are you reporting on?", CODE: "WID"},
                      QUESTIONS: [{QUESTION: "What kink of car to you want?", CODE: "WB", TYPE: LIST_OF_CHOICES,
                               CHOICE: ["Alpha romeo", "BMW", "Citroen", "DAF", "EXCALIBUR", "FIAT", "GMC", "Hummer",
                                        "INFINITI", "JAGUAR", "KIA", "LEXUS", "MAHINDRA", "NISSAN", "OPEL", "PORSCHE",
                                        "Q5 audi","ROVER", "SEAT", "TALBOT", "UMM", "VOLVO", "WESTFIELD", "X5 BM",
                                        "Yaris toyota", "Z06 Corvette", "1 Audi", "1 BUGATTI", "1 Cadillac", "1 DATSUN",
                                        "1 Eclipse Mazda", "1 Ford", "1 GUMPERT", "1 HONDA", "1 ISUZU", "1 JEEP", "1 KTM",
                                        "1 LANCIA", "1 Mercedes", "1 Navigator LINCOLN", "1 OLDSMOBILE", "1 Peugeot",
                                        "1 Quattro audi", "1 Renault", "1 Smart", "1 Toyota", "1 Uno fiat",
                                        "1 VolksWagen", "1 Willys", "1 Xantia citroen", "1 Yeti Skoda", "1 Zeta Lancia",
                                        "2 Austin", "2 Bellier", "2 Chevrolet", "2 Datsun", "2 Elandra hyundai",
                                        "2 Fisker", "2 Grecav", "2 Hyundai"],
                               ALLOWED_CHOICE: MULTIPLE_ANSWERS}],
                      CHARACTER_REMAINING: "65 / 160 characters used (1 SMS)",
                      SUCCESS_MSG: "Your questionnaire has been saved",
                      PAGE_TITLE: "Data Senders"}
