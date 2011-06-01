# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import mangrove.errors.MangroveException as ex


DEFAULT = "default"
WEB = "web"
SMS = "sms"
SUBMISSION = "submission"
REGISTRATION = "registration"

DEFAULT_EXCEPTION_MESSAGE = "An exception has occurred"

exception_messages = {


    ex.EntityTypeAlreadyDefined: {
        DEFAULT: "Entity identified by %s is already defined"},

    ex.EntityQuestionCodeNotSubmitted: {
        DEFAULT: "You have not created a question asking the collector for the subject he is reporting on"
    },

    ex.FormModelDoesNotExistsException: {
        DEFAULT: "Questionnaire ID %s doesnt exist.",
        WEB: "Error with Questionnaire ID %s. Find the Questionnaire ID on the printed questionnaire and resend SMS",
        SMS: "Error with Questionnaire ID %s. Find the Questionnaire ID on the printed questionnaire and resend SMS"
    },

    ex.DataObjectNotFound: {
        DEFAULT: "This entity reported on is not registered in our system. Please register entity or contact us at 033 20 426 89"
    },

    ex.NumberNotRegisteredException: {
        DEFAULT: "This telephone number is not registered in our system.",
        SMS: "This telephone number is not registered in our system. Please register or contact us at 033 20 426 89."
    },

    ex.QuestionCodeAlreadyExistsException: {
        DEFAULT: "Question Code Already Exists",
        WEB: "Question Code %s provided already exists"
    },

    ex.InvalidAnswerSubmissionException: {
        DEFAULT: "Error. Invalid Submission. Refer to printed Questionnaire. Resend the question ID and answer for: %s"
    },

    ex.EntityTypeDoesNotExistsException: {
        DEFAULT: "This entity %s reported on is not registered in our system. Please register entity or contact us at 033 20 426 89."
    },

    ex.NoQuestionsSubmittedException: {
        DEFAULT: "Please submit atleast one valid question code"
    }

}

VALIDATION_FAILURE_ERROR_MESSAGE = "Error. Invalid Submission. Refer to printed Questionnaire. Resend the question ID and answer for %s"

success_messages = {
    SUBMISSION: "Thank you %s for your data record. We successfully received your submission.",
    REGISTRATION: "Registration has been successful. The short code is %s."
}
