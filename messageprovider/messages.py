# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
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
        DEFAULT: u"Error. Invalid Submission. Refer to printed Questionnaire. Unique Identification Number(ID) is missing."
    },

    ex.FormModelDoesNotExistsException: {
        DEFAULT: u"Questionnaire ID %s doesnt exist.",
        WEB: u"Error with Questionnaire ID %s. Find the Questionnaire ID on the printed questionnaire and resend SMS",
        SMS: u"Error with Questionnaire ID %s. Find the Questionnaire ID on the printed questionnaire and resend SMS"
    },

    ex.DataObjectNotFound: {
        DEFAULT: u"This entity reported on is not registered in our system. Please register entity or contact us at 033 20 426 89"
    },

    ex.NumberNotRegisteredException: {
        DEFAULT: u"This telephone number is not registered in our system.",
        SMS: u"This telephone number is not registered in our system. Please register or contact us at 033 20 426 89."
    },

    ex.QuestionCodeAlreadyExistsException: {
        DEFAULT: u"Question Code Already Exists",
        WEB: u"Question Code %s provided already exists"
    },

    ex.InvalidAnswerSubmissionException: {
        DEFAULT: u"Error. Invalid Submission. Refer to printed Questionnaire. Resend the question ID and answer for: %s"
    },

    ex.EntityTypeDoesNotExistsException: {
        DEFAULT: u"This entity %s reported on is not registered in our system. Please register entity or contact us at 033 20 426 89."
    },

    ex.SMSParserInvalidFormatException: {
        DEFAULT: u"Invalid message format.",
        SMS: u"Invalid message format. Please submit the message in the format: <Questionnaire Code><SPACE>+<Question Code><SPACE><Answer>"
    },
    
    ex.NoQuestionsSubmittedException: {
        DEFAULT: u"Please submit atleast one valid question code"
    },

    ex.MultipleSubmissionsForSameCodeException:{
        DEFAULT: u"Error. Invalid Submission. Refer to printed Questionnaire. Multiple responses have been submitted for question code : %s"
    },
    ex.InactiveFormModelException:{
        DEFAULT: u"Error. You can not send us your answers for this questionnaire. The project is inactive. Please contact the administrator."
    }
}

VALIDATION_FAILURE_ERROR_MESSAGE = u"Error. Invalid Submission. Refer to printed Questionnaire. Resend the question ID and answer for %s"

success_messages = {
    SUBMISSION: u"Thank you %s. We received : ",
    REGISTRATION: u"Registration successful. %s."
}
