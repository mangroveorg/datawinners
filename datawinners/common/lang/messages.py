from couchdb.mapping import TextField, DictField
from mangrove.datastore.cache_manager import get_cache_manager
from mangrove.datastore.documents import DocumentBase

ACCOUNT_MESSAGE_DOC_ID = "account_message"

LANGUAGE_EXPIRY_TIME_IN_SEC = 2 * 60 * 60


def get_language_cache_key(dbm, language_code):
    return str("%s_%s" % (dbm.database.name, language_code))

class CustomizedMessage(DocumentBase):
    messages = DictField()

    def __init__(self, document_type, id, messages):
        DocumentBase.__init__(self, id=id, document_type=document_type)
        self.messages = messages


class QuestionnaireCustomizedMessages(CustomizedMessage):
    language_name = TextField()

    def __init__(self, lang_code, language, messages):
        super(QuestionnaireCustomizedMessages, self).__init__('CustomizedMessage', lang_code, messages)
        self.language_name = language


class AccountWideSMSMessage(CustomizedMessage):
    def __init__(self, messages):
        super(AccountWideSMSMessage, self).__init__('AccountWideMessage', ACCOUNT_MESSAGE_DOC_ID, messages)


def save_questionnaire_custom_messages(dbm, lang_code, messages, language=None):
    save_custom_messages(dbm, lang_code, messages, language)


def save_account_wide_sms_messages(dbm, account_messages):
    return save_custom_messages(dbm, ACCOUNT_MESSAGE_DOC_ID, account_messages)


def save_custom_messages(dbm, message_id, messages, language=None):
    message = dbm.database.get(message_id)
    if message:
        return _update_reply_message(dbm, message, messages, message_id)
    else:
        return _create_reply_message_template(dbm, message_id, messages, language)


def _update_reply_message(dbm, message, messages, message_id):
    message["messages"] = messages
    dbm.database.update([message])
    _delete_language_from_cache(dbm, message_id)
    return message_id

def _delete_language_from_cache(dbm, language_code):
    cache_manger = get_cache_manager()
    cache_key = get_language_cache_key(dbm, language_code)
    cache_manger.delete(cache_key)

def _create_reply_message_template(dbm, message_id, messages, language=None):
    if message_id == ACCOUNT_MESSAGE_DOC_ID:
        raise Exception
    message = QuestionnaireCustomizedMessages(message_id, language, messages)
    return dbm._save_document(message)


