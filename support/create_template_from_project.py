import sys

if __name__ == "__main__" and __package__ is None:
    sys.path.insert(0, ".")
import json
from datawinners.questionnaire.library import QuestionnaireLibrary
from mangrove.form_model.field import field_to_json


#Script which creates a template document given project details. Can be used for migrations.
def create_template_from_project(**kwargs):
    #dbm = get_db_manager("questionnaire_library")
    #_delete_db_and_remove_db_manager(dbm)
    library = QuestionnaireLibrary()
    library.create_template_from_project(**kwargs)

kwargs = {'db_name': 'hni_testorg_slx364903', 'category': 'Education', 'name': 'students details', 'id': 'stu_1',
          'form_code': '029'}

create_template_from_project(**kwargs)