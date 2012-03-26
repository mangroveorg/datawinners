# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils.translation import ugettext as _
import mangrove.errors.MangroveException as ex


DEFAULT = u"default"
WEB = u"web"
SMS = u"sms"
SUBMISSION = u"submission"
REGISTRATION = u"registration"

DEFAULT_EXCEPTION_MESSAGE = u"An exception has occurred"

exception_messages = {

    ex.EntityTypeAlreadyDefined: {
        DEFAULT: u"Entity identified by %s is already defined"},

    ex.EntityQuestionCodeNotSubmitted: {
        DEFAULT: u"Error. Invalid Submission. Refer to printed Questionnaire. Unique Identification Number(ID) is missing.",
        WEB: u"This field is required.",
        SMS: u"Error. Incorrect answer for %s. Please resend entire message."
    },

    ex.FormModelDoesNotExistsException: {
        DEFAULT: u"Questionnaire ID %s doesnt exist.",
        WEB: u"Error with Questionnaire code %s. Find the Questionnaire code on the printed questionnaire and resend SMS starting with this questionnaire code."
        ,
        SMS: u"Error with Questionnaire code %s. Find the Questionnaire code on the printed questionnaire and resend SMS starting with this questionnaire code."
    },

    ex.DataObjectNotFound: {
        DEFAULT: u"This entity reported on is not registered in our system. Please register entity or contact us at 033 20 426 89",
        WEB: u"This %s is not yet registered in the system. Please check the %s’s unique ID number and resubmit.",
        SMS: u"This %s %s is not registered in our system.Please register this %s or contact your supervisor."
    },

    ex.NumberNotRegisteredException: {
        DEFAULT: u"This telephone number is not registered in our system.",
        SMS: u"Your telephone number is not yet registered in our system. Please contact your supervisor."
    },

    ex.QuestionCodeAlreadyExistsException: {
        DEFAULT: u"Question Code Already Exists",
        WEB: u"Question Code %s provided already exists"
    },

    ex.InvalidAnswerSubmissionException: {
        DEFAULT: u"Error. Invalid Submission. Refer to printed Questionnaire. Resend the question ID and answer for: %s"
    },

    ex.EntityTypeDoesNotExistsException: {
        DEFAULT: u"Error. Incorrect answer for t. Please resend entire message."
    },

    ex.SMSParserInvalidFormatException: {
        DEFAULT: u"Invalid message format.",
        SMS: u"Error: SMS Incorrect. Review printed questionnaire and re-send SMS."
    },
    ex.SMSParserWrongNumberOfAnswersException: {
        DEFAULT: u"Error. Incorrect number of answers submitted. Review printed questionnaire and resend SMS.",
        SMS: u"Error. Incorrect number of answers submitted. Review printed questionnaire and resend SMS."
    },
    ex.SubmissionParseException: {
        DEFAULT: u"Invalid message format.",
        WEB: u"The system is experiencing a problem right now. Please try again in a few minutes",
        SMS: u"The system is unable to accept your SMS right now. Please wait one hour and resend the same message."
    },
    ex.NoQuestionsSubmittedException: {
        DEFAULT: u"Error: Invalid Submission. No valid question found. Check the Question Code on the printed questionnaire and resend SMS with the right Question code."
        ,
        SMS: u"Error: Invalid Submission. No valid question found. Check the Question Code on the printed questionnaire and resend SMS with the right Question code."

    },
    ex.MultipleSubmissionsForSameCodeException: {
        DEFAULT: u"Error. Incorrect answer for %s. Please resend entire message."
    },
    ex.InactiveFormModelException: {
        DEFAULT: u"Error. This project is not yet active. Submissions can be made only for an active project."
    },
    Exception: {
        DEFAULT: u"Error. Internal error. Please call technical support"
    }
}

def get_validation_failure_error_message():
    return _("Error. Incorrect answer for %s. Please resend entire message.")

def get_submission_success_message():
    return _("Thank you") + " %s. " + _("We received : ")

def get_registration_success_message():
    return _("Registration successful.") + " %s. "

def get_wrong_number_of_answer_error_message():
    return _("Error. Incorrect number of answers submitted. Review printed questionnaire and resend SMS.")