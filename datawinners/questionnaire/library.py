import json
import os
from couchdb.mapping import TextField
from mangrove.datastore.cache_manager import get_cache_manager
from mangrove.datastore.documents import FormModelDocument, DocumentBase, attributes
from mangrove.form_model.form_model import get_form_model_by_code
from datawinners.main.database import get_db_manager

TEMPLATE_CACHE_EXPIRY_TIME_IN_SEC = 2 * 60 * 60
GROUPING_CACHE_KEY = 'template_grouping_cache_key'


class QuestionnaireTemplateDocument(FormModelDocument):
    category = TextField()
    description = TextField()

    def __init__(self, name, category, language='en', description=None, id=None):
        DocumentBase.__init__(self, id=id, document_type='QuestionnaireTemplate')
        self.category = category
        self.description = description
        self.name = name
        self.language = language


class QuestionnaireLibrary:
    def __init__(self):
        self.dbm = get_db_manager("questionnaire_library")
        self.cache_manger = get_cache_manager()

    def get_questionnaire_template(self, template_id):
        key_as_str = self.get_question_template_key(template_id)
        template_doc = self.cache_manger.get(key_as_str)
        if template_doc is None:
            template_doc = self.dbm._load_document(template_id)
            self.cache_manger.set(key_as_str, template_doc, time=TEMPLATE_CACHE_EXPIRY_TIME_IN_SEC)
        return template_doc.unwrap()

    def get_template_groupings(self):
        return self._grouping()

    def _grouping(self):
        rows = self.dbm.load_all_rows_in_view('by_template_category')
        categories = set([a['key'] for a in rows])
        result = []
        for category in categories:
            template = {}
            values = self._get_values_for_key(category, rows)
            template.update({'category': category})
            template.update({'templates': values})
            result.append(template)
        return result

    def _get_values_for_key(self, key, rows):
        values = []
        for row in rows:
            if row['key'] == key:
                values.append(row['value'])
        return values

    def get_question_template_key(self, template_id):
        assert template_id is not None
        return str("%s_%s" % (self.dbm.database.name, template_id))
