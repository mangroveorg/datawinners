# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from django.utils.translation import ugettext as _
import mangrove.errors.MangroveException as ex
import string


DEFAULT = u"default"
WEB = u"web"
SMS = u"sms"
SUBMISSION = u"submission"
REGISTRATION = u"registration"
SMART_PHONE=u"smartPhone"

NOT_AUTHORIZED_DATASENDER_MSG = "Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor."
SUBMISSION_LIMIT_REACHED_MSG = "You have reached your limit of 1000 free Submissions. Ask your Project Manager to sign up for a monthly subscription to continue submitting data."
SMS_LIMIT_REACHED_MSG = "You have reached your 50 SMS Submission limit. Please upgrade to a monthly subscription to continue sending in SMS Submissions to your Questionnaires."

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
        WEB: u"Error. Questionnaire Code %s is incorrect. Please review the Registration Form and resend entire SMS.",
        SMS: u"Error. Questionnaire Code %s is incorrect. Find the Code on the top of the printed Questionnaire and resend SMS starting with this Code."
    },

    ex.DataObjectNotFound: {
        DEFAULT: u"This entity reported on is not registered in our system. Please register entity or contact us at 033 20 426 89",
        WEB: u"This %s is not yet registered in the system. Please check the %s’s unique ID number and resubmit.",
        SMS: u"Error. %s %s is not registered. Check the Identification Number and resend entire SMS or contact your supervisor."
    },

    ex.NumberNotRegisteredException: {
        DEFAULT: u"This telephone number is not registered in our system.",
        SMS: u"Error. You are not authorized to submit data for this Questionnaire. Please contact your supervisor."
    },

    ex.QuestionCodeAlreadyExistsException: {
        DEFAULT: u"Question Code Already Exists",
        WEB: u"Question Code %s provided already exists"
    },

    ex.QuestionAlreadyExistsException: {
        DEFAULT: u"Question Already Exists",
        WEB: u"Question %s provided already exists"
    },

    ex.InvalidAnswerSubmissionException: {
        DEFAULT: u"Error. Invalid Submission. Refer to printed Questionnaire. Resend the question ID and answer for: %s"
    },

    ex.EntityTypeDoesNotExistsException: {
        DEFAULT: u"Error. Incorrect answer for t. Please resend entire message."
    },

    ex.SMSParserInvalidFormatException: {
        DEFAULT: u"Invalid message format.",
        SMS: u"Error: SMS Incorrect. Please review printed questionnaire and resend entire SMS."
    },
    ex.SMSParserWrongNumberOfAnswersException: {
        DEFAULT: u"Error. Incorrect number of responses. Review printed Questionnaire and resend entire SMS.",
        SMS: u"Error. Incorrect number of responses. Review printed Questionnaire and resend entire SMS."
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
    Exception: {
        DEFAULT: u"Error. Internal error. Please call technical support"
    }
}

def get_validation_failure_error_message(response):
    if response.is_registration:
        return _("Error. Incorrect answer for %s. Please review the Registration Form and resend entire SMS.")
    else:
        return _("Error. Incorrect answer for %s. Please review printed Questionnaire and resend entire SMS.")

def get_submission_success_message(response):
    datasender = response.reporters[0].get('name').split()[0].capitalize()
    return _("Thank you %(datasender)s. We received your SMS") % {'datasender': datasender}

def get_registration_success_message(response):
    datasender = response.reporters[0].get('name').split()[0].capitalize() if len(response.reporters) else ''
    subject_type = response.entity_type[0]
    return _("Thank you %(datasender)s, We registered your %(subject_type)s") % \
           {'datasender':datasender, 'subject_type':subject_type}

def get_wrong_number_of_answer_error_message():
    return _("Error. Incorrect number of responses. Please review printed Questionnaire and resend entire SMS.")


def get_datasender_not_linked_to_project_error_message():
    return _(NOT_AUTHORIZED_DATASENDER_MSG)

def get_subject_info(response, form_model):
    subject_name = ''
    if form_model:
        if response.is_registration:
            subject_name = get_response_by_question_name(response, form_model, 'name')
            subject_name = "%s %s" % (get_response_by_question_name(response, form_model, 'firstname'), subject_name)
        elif 'firstname' in response.subject.data:
            subject_name = "%s %s" % (response.entity_type[0], response.subject.data.get('firstname')['value'])
    return "%s (%s)" % (string.capwords(subject_name), response.short_code)

def get_response_by_question_name(response, form_model, question_name):
    field = form_model.get_field_by_name(question_name)
    if not field: return ''
    return response.processed_data.get(field.code)