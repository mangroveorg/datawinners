from django.core.mail import mail_admins

def mail_feed_errors(response):
    if response.feed_error_message:
        subject = 'Error while creating feed doc for survey_response id %s ' % response.survey_response_id
        mail_admins(subject, response.feed_error_message)
