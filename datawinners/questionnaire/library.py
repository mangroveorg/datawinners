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

    def _create_view(self):
        from datawinners.main.utils import find_views

        views = find_views('questionnaire_template_view')
        for view_name, view_def in views.iteritems():
            map_function = (view_def['map'] if 'map' in view_def else None)
            reduce_function = (view_def['reduce'] if 'reduce' in view_def else None)
            self.dbm.create_view(view_name, map_function, reduce_function)

    def _grouping(self):
        rows = self.dbm.load_all_rows_in_view('by_template_category', group=True, reduce=True)
        result = []
        for row in rows:
            template_data = {'category': row['key'], 'templates': self._construct_template_data(row['value'])}
            result.append(template_data)
        return result

    def _construct_template_data(self, values):
        details = []
        for value in values:
            details.append({'name': value[0], 'id': value[1]})
        return details

    def get_question_template_key(self, template_id):
        assert template_id is not None
        return str("%s_%s" % (self.dbm.database.name, template_id))

    def create_template_from_project(self, file_name):
        self._create_view()
        full_path = os.path.realpath(__file__)
        path = os.path.dirname(full_path)+'/'+file_name
        docs = []
        with open(path) as data_file:
            questionnaires = json.load(data_file)
            for data in questionnaires:
                template_doc = QuestionnaireTemplateDocument(name=data.get('name'), category=data.get('category'))
                template_doc.json_fields = data.get('json_fields')
                template_doc.validators = data.get('validators')
                doc_id = self.dbm._save_document(template_doc)
                docs.append(doc_id)
        return docs

    def get_category_mapping(self):
        map = {}
        map.update({'Health':
                        ['Monthly Client Report', 'Monthly Stock Report', 'Patient Interview',
                         'Weekly Sentinel Site Survey']})
        map.update({'Food Security': ['Waybill Sent', 'Waybill Received']})
        map.update({'Education': ['Student Census', 'Grant Reception', 'Textbook Reception', 'Standardized Test Results',
                                  'Early Grade Reading Assessment']})
        map.update({'Early Warning': ['Weekly assessment', 'Fast Onset']})
        map.update({'Agriculture': ['Livestock Census']})
        map.update({'Commercial': ['Invoice']})
        map.update({'Socio-Economic': ['Household Survey']})
        return map