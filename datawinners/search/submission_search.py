from collections import OrderedDict
import elasticutils
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.form_model.form_model import header_fields
from datawinners.search.query import QueryBuilder, Query


class SubmissionQueryBuilder(QueryBuilder):
    def create_paginated_query(self, doc_type, database_name, query_params):
        query = super(SubmissionQueryBuilder, self).create_paginated_query(doc_type, database_name, query_params)
        if query_params.get('filter'):
            query = query.filter(status=query_params.get('filter'))
        return query

    def create_query(self, doc_type, database_name):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes(doc_type)

class SubmissionQueryResponseCreator():
    def create_response(self, required_field_names, query):
        submissions = []
        for res in query.values_dict(tuple(required_field_names)):
            subject = []
            subject.append(res._id)
            subject.append([res.get('ds_name'), res.get('ds_id')])

            for key in required_field_names:
                if not key in ['ds_id', 'ds_name']:
                    if (isinstance(res.get(key), dict)):
                        subject.append(res.get(key).values())
                    else:
                        subject.append(res.get(key))
            submissions.append(subject)
        return submissions


class SubmissionQuery(Query):
    def __init__(self, form_model,query_params):
        Query.__init__(self, SubmissionQueryResponseCreator(), SubmissionQueryBuilder(),query_params)
        self.form_model = form_model

    def get_headers(self, user, form_code):
        header_dict = OrderedDict()
        self._update_static_header_info(header_dict)

        def key_attribute(field): return field.code.lower()

        header_dict = header_fields(self.form_model, key_attribute, header_dict)
        if "reporter"  in self.form_model.entity_type:
            header_dict.pop(self.form_model.entity_question.code)
        return header_dict

    def _update_static_header_info(self, header_dict):
        header_dict.update({"ds_id": "Datasender Id"})
        header_dict.update({"ds_name": "Datasender Name"})
        header_dict.update({"date": "Submission S Date"})
        submission_type = self.query_params.get('filter')
        if not submission_type:
            header_dict.update({"status": "Status"})
        else:
            if submission_type is 'error':
                header_dict.update({"error_msg": "Error Message"})
        header_dict.update({self.form_model.entity_question.code: "Entity"})
        header_dict.update({self.form_model.event_time_question.code:"Reporting Date"})


    def populate_query_options(self):
        options = super(SubmissionQuery, self).populate_query_options()
        try:
            options.update({'filter': self.query_params["filter"]})
        except KeyError:
            pass
        return options

