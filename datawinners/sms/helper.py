import re
from datawinners.accountmanagement.models import TEST_REPORTER_MOBILE_NUMBER
from datawinners.project.helper import logger
from datawinners.scheduler.smsclient import SMSClient
from datawinners.sms.models import MSG_TYPE_USER_MSG


def broadcast_message(data_sender_phone_numbers, message, organization_tel_number, other_numbers, message_tracker,
                      country_code=None):
    """

    :param data_sender_phone_numbers:
    :param message:
    :param organization_tel_number:
    :param other_numbers:
    :param message_tracker:
    :param country_code:
    :return:
    """
    sms_client = SMSClient()
    sms_sent = None
    failed_numbers = []
    for phone_number in data_sender_phone_numbers:
        if phone_number is not None and phone_number != TEST_REPORTER_MOBILE_NUMBER:
            logger.info(("Sending broadcast message to %s from %s") % (phone_number, organization_tel_number))
            sms_sent = sms_client.send_sms(organization_tel_number, phone_number, message, MSG_TYPE_USER_MSG)
        if sms_sent:
            message_tracker.increment_message_count_for(send_message_count=1)
        else:
            failed_numbers.append(phone_number)

    for number in other_numbers:
        number = number.strip()
        number_with_country_prefix = number
        if country_code:
            number_with_country_prefix = "%s%s" % (country_code, re.sub(r"^[ 0]+", "", number))

        logger.info(("Sending broadcast message to %s from %s") % (number_with_country_prefix, organization_tel_number))
        sms_sent = sms_client.send_sms(organization_tel_number, number_with_country_prefix, message, MSG_TYPE_USER_MSG)
        if sms_sent:
            message_tracker.increment_message_count_for(send_message_count=1)
        else:
            failed_numbers.append(number)

    return failed_numbers