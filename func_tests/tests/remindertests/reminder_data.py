WARNING_MESSAGE = "warning_message"
PROJECT_NAME = "project_name"
DEADLINE = "deadline"
FREQUENCY = "frequency"
TYPE = "type"
WEEK = "Week"
DAY = "day"
WEEK_DAY = [' ', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
SAME_WEEK = "Same week"
FOLLOWING_WEEK = "Following week"
MONTH = "Month"
MONTH_DAY = [" ", "1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th", "13th", "14th",
             "15th", "16th", "17th", "18th", "19th", "20th", "21st", "22nd", "23rd", "24th", "25th", "26th", "27th",
             "28th", "29th", "30th", "Last Day"]
SAME_MONTH = "Same month"
FOLLOWING_MONTH = "Following month"
EXAMPLE_TEXT = "example_text"
MESSAGE = "message"
ON_DEADLINE = u"on_deadline"
BEFORE_DEADLINE = u"before_deadline"
AFTER_DEADLINE = u"after_deadline"
REMINDER_DEADLINE = "reminder_mode"
REMINDERS = "reminders"
WHOM_TO_SEND = "whom_to_send"
ALL = "all"
DEFAULTERS = "defaulters"
SUCCESS_MESSAGE = "Reminder settings saved successfully."
ERROR_MESSAGE = "error_message"

warning = "You can add Reminders here, however this feature is not available to Trial account users. Sign up for a monthly subscription to send Reminders to your Data Senders."

DISABLED_REMINDER = {PROJECT_NAME: "clinic test project", WARNING_MESSAGE: warning}

DEADLINE_FIRST_DAY_OF_SAME_WEEK = {PROJECT_NAME: "clinic test project",
                                   DEADLINE: {FREQUENCY: WEEK, DAY: WEEK_DAY[1], TYPE: SAME_WEEK,
                                              EXAMPLE_TEXT: "Example: Monday of the reporting week"}}
DEADLINE_LAST_DAY_OF_SAME_WEEK = {DEADLINE: {FREQUENCY: WEEK, DAY: WEEK_DAY[7], TYPE: SAME_WEEK,
                                             EXAMPLE_TEXT: "Example: Sunday of the reporting week"}}

DEADLINE_SECOND_DAY_OF_FOLLOWING_WEEK = {DEADLINE: {FREQUENCY: WEEK, DAY: WEEK_DAY[2], TYPE: FOLLOWING_WEEK,
                                                    EXAMPLE_TEXT: "Example: Tuesday of the week following the reporting week"}}
DEADLINE_FIFTH_DAY_OF_FOLLOWING_WEEK = {DEADLINE: {FREQUENCY: WEEK, DAY: WEEK_DAY[5], TYPE: FOLLOWING_WEEK,
                                                   EXAMPLE_TEXT: "Example: Friday of the week following the reporting week"}}

DEADLINE_FIRST_DAY_OF_SAME_MONTH = {PROJECT_NAME: "clinic test project",
                                    DEADLINE: {FREQUENCY: MONTH, DAY: MONTH_DAY[1], TYPE: SAME_MONTH,
                                               EXAMPLE_TEXT: "Example: 1st of October for October report"}}
DEADLINE_LAST_DAY_OF_SAME_MONTH = {DEADLINE: {FREQUENCY: MONTH, DAY: MONTH_DAY[31], TYPE: SAME_MONTH,
                                              EXAMPLE_TEXT: "Example: Last Day of October for October report"}}

DEADLINE_TWENTIETH_DAY_OF_FOLLOWING_MONTH = {DEADLINE: {FREQUENCY: MONTH, DAY: MONTH_DAY[20], TYPE: FOLLOWING_MONTH,
                                                        EXAMPLE_TEXT: "Example: 20th of October for September report"}}
DEADLINE_ELEVENTH_DAY_OF_FOLLOWING_MONTH = {DEADLINE: {FREQUENCY: MONTH, DAY: MONTH_DAY[11], TYPE: FOLLOWING_MONTH,
                                                       EXAMPLE_TEXT: "Example: 11th of October for September report"}}

REMINDER_DATA_WEEKLY = {PROJECT_NAME: "clinic13 test project",
                        DEADLINE: {FREQUENCY: WEEK, DAY: WEEK_DAY[7], TYPE: SAME_WEEK,
                                   EXAMPLE_TEXT: "Example: Sunday of the reporting week"},
                        REMINDERS: {DAY: 1, MESSAGE: u"One day remaining, please submit the data",
                                    REMINDER_DEADLINE: BEFORE_DEADLINE},
                        WHOM_TO_SEND: ALL}

REMINDER_DATA_MONTHLY = {PROJECT_NAME: "clinic13 test project",
                         DEADLINE: {FREQUENCY: MONTH, DAY: MONTH_DAY[31], TYPE: FOLLOWING_MONTH,
                                    EXAMPLE_TEXT: "Example: Last Day of October for September report"},
                         REMINDERS: [{DAY: 10, MESSAGE: u"10 days remaining, please submit the data",
                                      REMINDER_DEADLINE: BEFORE_DEADLINE},
                                     {DAY: 0, MESSAGE: u"Today is the deadline, please submit the data",
                                      REMINDER_DEADLINE: ON_DEADLINE},
                                     {DAY: 5, MESSAGE: u"5 days overdue, please submit the data",
                                      REMINDER_DEADLINE: AFTER_DEADLINE}],
                         WHOM_TO_SEND: DEFAULTERS}

MESSAGE_LONGER_THAN_160 = "2 day(s) are remainning to deadline. Please send your data for Clinic Test Project. 2 day(s) are remainning to deadline. Please send your data for Clinic Test Project."