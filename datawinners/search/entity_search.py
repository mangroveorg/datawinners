from collections import OrderedDict
import elasticutils
from datawinners.entity.helper import get_entity_type_fields
from datawinners.main.database import get_database_manager
from mangrove.form_model.form_model import header_fields, get_form_model_by_entity_type, get_form_model_by_code
from datawinners.settings import ELASTIC_SEARCH_URL


class QueryBuilder():
    def __init__(self):
        self.elastic_utils_helper = ElasticUtilsHelper()

    def create_query(self, doc_type, database_name):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes(doc_type) #\
            #.filter(void=False)

    def create_paginated_query(self, doc_type, database_name, query_params):
        start_result_number = query_params.get("start_result_number")
        number_of_results = query_params.get("number_of_results")
        order = query_params.get("order")
        order_by = query_params.get("order_field")

        query = self.create_query(doc_type, database_name)
        if order_by: query.order_by(order + order_by + "_value")
        return query [start_result_number:start_result_number + number_of_results]

    def add_query_criteria(self, query_fields, query_text, search):
        if query_text:
            query_text_escaped = self.elastic_utils_helper.replace_special_chars(query_text)
            raw_query = {
                "query_string": {
                    "fields": tuple(query_fields),
                    "query": query_text_escaped
                }
            }
            return search.query_raw(raw_query)

        return search.query()


class ElasticUtilsHelper():
    def replace_special_chars(self, search_text):
        lucene_special_chars = ['\\', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']', '^', '"', '~', '*', '?',
                                '/',
                                ':']
        for char in lucene_special_chars:
            search_text = search_text.replace(char, '\\' + char)
        return search_text


class Query():
    def __init__(self, response_creator):
        self.elastic_utils_helper = ElasticUtilsHelper()
        self.query_builder = QueryBuilder()
        self.response_creator = response_creator

    def _getDatabaseName(self, user):
        return get_database_manager(user).database_name

    def get_headers(self, user, entity_type):
        pass

    def paginated_query(self, user, entity_type, query_params):
        entity_headers = self.get_headers(user, entity_type)
        options = {
            "start_result_number": query_params["start_result_number"],
            "number_of_results": query_params["number_of_results"],
            "order": query_params["order"]
        }
        if query_params["order_by"] > 0:
            options.update({"order_field": entity_headers[query_params["order_by"]]})

        paginated_query = self.query_builder.create_paginated_query(entity_type, self._getDatabaseName(user), options)
        query_with_criteria = self.query_builder.add_query_criteria(entity_headers, query_params["search_text"],
                                                                    paginated_query)
        entities = self.response_creator.create_response(entity_headers, query_with_criteria)
        return query_with_criteria.count(), paginated_query.count(), entities


class DatasenderQuery(Query):
    def __init__(self):
        Query.__init__(self, DatasenderQueryResponseCreator())

    def get_headers(self, user, entity_type=None):
        fields, old_labels, codes = get_entity_type_fields(get_database_manager(user))
        fields.append("devices")
        fields.append('projects')
        return fields


class SubjectQuery(Query):
    def __init__(self):
        Query.__init__(self, SubjectQueryResponseCreator())

    def get_headers(self, user, subject_type):
        manager = get_database_manager(user)
        form_model = get_form_model_by_entity_type(manager, [subject_type])
        return header_fields(form_model).keys()

    def query(self, user, subject_type, query_text):
        subject_headers = self.get_headers(user, subject_type)
        query = self.query_builder.create_query(subject_type, self._getDatabaseName(user))
        query_all_results = query[:query.count()]
        query_with_criteria = self.query_builder.add_query_criteria(subject_headers, query_text, query_all_results)
        subjects = self.response_creator.create_response(subject_headers, query_with_criteria)
        return subjects


class SubjectQueryResponseCreator():
    def create_response(self, required_field_names, query):
        subjects = []
        for res in query.values_dict(tuple(required_field_names)):
            subject = []
            for key in required_field_names:
                subject.append(res.get(key))
            subjects.append(subject)
        return subjects


class DatasenderQueryResponseCreator():
    def create_response(self, required_field_names, query):
        datasenders = []
        for res in query.values_dict(tuple(required_field_names)):
            result = []
            for key in required_field_names:
                if key is "devices":
                    self.add_check_symbol_for_row(res, result)
                else:
                    result.append(res.get(key))
            datasenders.append(result)
        return datasenders

    def add_check_symbol_for_row(self, datasender, result):
        check_img = '<img alt="Yes" src="/media/images/right_icon.png">'
        # result.extend([check_img])
        if datasender["email"]:
            result.extend([check_img + "&nbsp;" + check_img + "&nbsp;" + check_img])
        else:
            result.extend([check_img])


class SubmissionQueryResponseCreator():
    def create_response(self, required_field_names, query):
        subjects = []
        for res in query.values_dict(tuple(required_field_names)):
            subject = []
            subject.append(res._id)
            subject.append([res.get('ds_name'),res.get('ds_id')])

            for key in required_field_names:
             if not key  in ['ds_id' ,'ds_name'] :
                if(isinstance(res.get(key),dict)):
                    subject.append(res.get(key).values())
                else:
                    subject.append(res.get(key))
            subjects.append(subject)
        return subjects


class SubmissionQuery(Query):
    def __init__(self, form_model):
        Query.__init__(self, SubmissionQueryResponseCreator())
        self.form_model = form_model

    def get_headers(self,user, form_code):
        header_dict = OrderedDict()
        self._update_static_header_info(header_dict)
        def key_attribute(field): return field.code.lower()
        header_dict = header_fields(self.form_model, key_attribute, header_dict)
        return header_dict

    def _update_static_header_info(self, header_dict):
        header_dict.update({"ds_id": "Datasender Id"})
        header_dict.update({"ds_name": "Datasender Name"})
        header_dict.update({"date": "Submission Date"})
        header_dict.update({"status": "Status"})
        header_dict.update({"eid": "Entity"})
        header_dict.update({"rd": "Reporting Date"})

