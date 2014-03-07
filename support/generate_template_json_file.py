import json
import os
from mangrove.form_model.field import field_to_json
from mangrove.form_model.form_model import FormModel
from datawinners.main.database import get_db_manager
from datawinners.project.models import get_all_projects, Project


def generate_template_data():
    templates = []
    test_dbm = get_db_manager('hni_testorg_slx364903')
    projects = get_all_projects(test_dbm)
    for doc in projects:
        project = Project.load(test_dbm.database, doc.id)
        if project.language == 'en':
            json_obj = {}
            json_obj.update({u"name": unicode(project.name)})
            json_obj.update({u"language": unicode(project.language)})
            json_obj.update({u"category": _get_category(project.name)})
            form_model = FormModel.get(test_dbm, project.qid)
            fields = _remove_entity_field(form_model)
            json_obj.update({"json_fields": [field_to_json(f) for f in fields]})
            json_obj.update({"validators": [validator.to_json() for validator in form_model.validators]})
            templates.append(json_obj)

    file = os.path.dirname(__file__)+'/../datawinners/questionnaire/template_data.json'
    with open(file, 'w') as outfile:
        json.dump(templates, outfile, indent=4)


def _get_category(project_name):
    project_name = project_name.strip()
    project_to_category_map = get_category_mapping()
    for category, project_names in project_to_category_map.iteritems():
        if project_name in [name.lower() for name in project_names]:
            return category


def _remove_entity_field(form_model):
    return [each for each in form_model.fields if not each.is_entity_field]


def get_category_mapping():
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

generate_template_data()