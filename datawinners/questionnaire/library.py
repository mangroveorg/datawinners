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

    def create_template(self, id):
        template_doc = QuestionnaireTemplateDocument(name='patient records', category='Health', id=id)
        test_dbm = get_db_manager('hni_testorg_slx364903')
        form_model = get_form_model_by_code(test_dbm, '025')
        template_doc.json_fields = [f._to_json() for f in form_model.fields]
        template_doc.validators = [validator.to_json() for validator in form_model.validators]
        self.dbm._save_document(template_doc)

    def get_questionnaire_template(self, template_id):
        template_doc = self.dbm._load_document(template_id)
        return template_doc.unwrap()

    def get_templates(self):

        pass
