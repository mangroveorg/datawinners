from django.core.mail import mail_admins

def mail_feed_errors(response, database_name):
    if response.feed_error_message:
        subject = '[Feed] Error while creating/updating feed doc for survey_response id %s in db %s ' % (
        response.survey_response_id, database_name)
        mail_admins(subject, response.feed_error_message)
