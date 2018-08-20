import cgi
from copy import copy
import elasticutils

from datawinners.search.index_utils import es_questionnaire_field_name
from mangrove.form_model.form_model import header_fields, get_form_model_by_entity_type
from mangrove.form_model.form_model import REPORTER
from datawinners.main.database import get_database_manager
from datawinners.search.query import Query, QueryBuilder
from mangrove.form_model.project import get_entity_type_fields


DATASENDER_DISPLAY_FIELD_ORDER = ['name', 'mobile_number', 'email', 'location', 'geo_code', 'short_code', 'projects',
                                'devices', 'customgroups', 'groups']
class SubjectQuery(Query):
    def __init__(self, query_params=None):
        Query.__init__(self, SubjectQueryResponseCreator(), QueryBuilder(), query_params)

    def get_headers(self, user, subject_type):
        manager = get_database_manager(user)
        form_model = get_form_model_by_entity_type(manager, [subject_type])
        subject_es_headers = []
        for code in header_fields(form_model, key_attribute='code').keys():
            subject_es_headers.append(es_questionnaire_field_name(code, form_model.id))
        return subject_es_headers

    def query(self, user, subject_type, query_text):
        subject_headers = self.get_headers(user, subject_type)
        query = self.query_builder.get_query(database_name=self._getDatabaseName(user), doc_type=subject_type)
        query_all_results = query[:query.count()]
        query_with_criteria = self.query_builder.add_query_criteria(subject_headers, query_all_results, query_text)
        subjects = self.response_creator.create_response(subject_headers, query_with_criteria)
        return subjects


class SubjectQueryResponseCreator():
    def create_response(self, required_field_names, query):
        subjects = []
        for res in query.values_dict():
            subject = []
            for key in required_field_names:
                value = res.get(key)
                if res.get(key+'_unique_code'):
                    value += "<span class='small_grey'>  %s</span>" % res.get(key+'_unique_code')
                subject.append(value)
            subjects.append(subject)
        return subjects


class DatasenderQueryResponseCreator():
    def _format_contact_groups(self, key, res, result):
        groups = getattr(res, key, None)
        if groups:
            result.append(", ".join(groups))
        else:
            result.append("")

    def create_response(self, search_results, show_projects=True):
        required_field_names = copy(DATASENDER_DISPLAY_FIELD_ORDER)

        if not show_projects:
            required_field_names.remove('projects')

        datasenders = []
        for res in search_results.hits:
            result = []
            for key in required_field_names:
                if key is "devices":
                    self.add_check_symbol_for_row(res, result)
                elif key in ["projects", "customgroups"]:
                    values_joined = ", ".join(getattr(res, key, []))
                    result.append(cgi.escape(values_joined))
                elif key is "groups":
                    self._format_contact_groups(key, res, result)
                else:
                    result.append(getattr(res, key, ''))
            datasenders.append(result)
        return datasenders

    def add_check_symbol_for_row(self, datasender, result):
        check_img = '<img alt="Yes" src="/media/images/right_icon.png" class="device_checkmark">'
        if getattr(datasender, 'email', None):
            result.extend([check_img + check_img + check_img])
        else:
            result.extend([check_img])

