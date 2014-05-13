from couchdb.mapping import TextField, DictField, Mapping
from django.utils.translation import ugettext
from mangrove.datastore.documents import DocumentBase


class CustomizedMessages(DocumentBase):
    _id = TextField()
    messages = DictField()

    def __init__(self, lang, messages):
        DocumentBase.__init__(self, document_type='CustomizedMessage')
        self._id = lang
        self.messages = messages


def render_text(template, context):
    return template


def get_message(dbm, lang, code, context={}):
    try:
        template = dbm.database.get(lang)["messages"][code]
    except Exception as e:
        template = ugettext(code)
    return render_text(template, context)


def save_messages(dbm, lang, value_dict):
    message = dbm.database.get(lang)
    if message:
        message["messages"] = value_dict
        dbm.database.update([message])
    else:
        message = CustomizedMessages(lang, value_dict)
        dbm._save_document(message)
