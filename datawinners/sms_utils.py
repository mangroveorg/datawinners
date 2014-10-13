from datawinners.sms.models import SMS


def log_sms(to_tel, from_tel, message, organization, message_id, transport_name, message_type):
    SMS(message= message,
        message_id=message_id,
        organization=organization,
        msg_from = from_tel,
        msg_to= to_tel,
        smsc = transport_name,
        msg_type = message_type,
        status="Submitted").save()