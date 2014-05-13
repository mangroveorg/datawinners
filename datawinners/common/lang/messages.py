from couchdb.mapping import TextField, DictField, Mapping
from django.utils.translation import ugettext
from mangrove.datastore.documents import DocumentBase


class CustomizedMessages(DocumentBase):
    _id = TextField()
    messages = DictField()
    language_name = TextField()

    def __init__(self, lang_code,language, messages):
        DocumentBase.__init__(self, document_type='CustomizedMessage')
        self._id = lang_code
        self.language_name = language
        self.messages = messages


def render_text(template, context):
    return template


def get_message(dbm, lang, code, context={}):
    try:
        template = dbm.database.get(lang)["messages"][code]
    except Exception as e:
        template = ugettext(code)
    return render_text(template, context)


def save_messages(dbm, lang_code, language ,value_dict):
    message = dbm.database.get(lang_code)
    if message:
        message["messages"] = value_dict
        dbm.database.update([message])
    else:
        message = CustomizedMessages(lang_code,language, value_dict)
        dbm._save_document(message)
