from couchdb.mapping import TextField
from mangrove.datastore.documents import FormModelDocument, DocumentBase, attributes
from mangrove.form_model.form_model import get_form_model_by_code
from datawinners.main.database import get_db_manager


class QuestionnaireTemplateDocument(FormModelDocument):
    category = TextField()
    description = TextField()

    def __init__(self, name, category, description=None, id=None):
        DocumentBase.__init__(self, id=id, document_type='QuestionnaireTemplate')
        self.category = category
        self.description = description
        self.name = name


class QuestionnaireLibrary:
    def __init__(self):
        self.dbm = get_db_manager("questionnaire_library")
        self.create_view()

    def create_template_from_project(self, category, name, id, form_code):
        template_doc = QuestionnaireTemplateDocument(name=name, category=category, id=id)
        test_dbm = get_db_manager('hni_testorg_slx364903')
        form_model = get_form_model_by_code(test_dbm, form_code)
        template_doc.json_fields = [f._to_json() for f in form_model.fields]
        template_doc.validators = [validator.to_json() for validator in form_model.validators]
        self.dbm._save_document(template_doc)

    def get_questionnaire_template(self, template_id):
        template_doc = self.dbm._load_document(template_id)
        return template_doc.unwrap()

    def create_view(self):
        from datawinners.main.utils import find_views
        views = find_views('questionnaire_template_view')
        for view_name, view_def in views.iteritems():
            map_function = (view_def['map'] if 'map' in view_def else None)
            self.dbm.create_view(view_name, map_function, None)

    def get_template_groupings(self):
        rows = self.dbm.load_all_rows_in_view('template_category')
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