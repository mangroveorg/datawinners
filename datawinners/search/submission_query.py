from collections import OrderedDict
import elasticutils
from datawinners.search.filters import SubmissionDateRangeFilter, ReportingDateRangeFilter
from datawinners.search.submission_index import es_field_name
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.form_model.form_model import header_fields
from datawinners.search.query import QueryBuilder, Query


class SubmissionIndexConstants:
    DATASENDER_ID_KEY = "ds_id"
    DATASENDER_NAME_KEY = "ds_name"


class SubmissionQueryBuilder(QueryBuilder):
    def __init__(self, form_model=None):
        QueryBuilder.__init__(self)
        self.form_model = form_model

    def create_query(self, database_name, *doc_type):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes(*doc_type)

    def filter_by_submission_type(self, query, query_params):
        submission_type_filter = query_params.get('filter')
        if submission_type_filter:
            if submission_type_filter == 'deleted':
                return query.filter(void=True)
            query = (query.filter(status=submission_type_filter))
        return query.filter(void=False)

    def create_paginated_query(self, query, query_params):
        query = super(SubmissionQueryBuilder, self).create_paginated_query(query, query_params)

        return self.filter_by_submission_type(query, query_params)

    def add_query_criteria(self, query_fields, query_text, query, query_params=None):
        query = super(SubmissionQueryBuilder, self).add_query_criteria(query_fields, query_text, query, query_params)
        search_filter_param = query_params.get('search_filters')
        if search_filter_param:
            submission_date_range = search_filter_param.get("submissionDatePicker")
            reporting_date_range = search_filter_param.get("reportingPeriodPicker")
            query = SubmissionDateRangeFilter(submission_date_range).build_filter_query(query)
            query = ReportingDateRangeFilter(reporting_date_range, self.form_model).build_filter_query(query)
            datasender_filter = search_filter_param.get("datasenderFilter")
            if datasender_filter:
                query = query.filter(ds_id=datasender_filter)
            subjectFilter = search_filter_param.get("subjectFilter")
            if subjectFilter:
                query = query.filter(entity_short_code = subjectFilter)
        return query

    def query_all(self, database_name, **kwargs):
        query = self.create_query(database_name, self.form_model.id)
        query_all_results = query[:query.count()]
        return query_all_results.filter(**kwargs)


class SubmissionQueryResponseCreator():
    def __init__(self, form_model):
        self.form_model = form_model

    def create_response(self, required_field_names, query):
        submissions = []
        for res in query.values_dict(tuple(required_field_names)):
            submission = [res._id, [res.get('ds_name') + "<span class='small_grey'>  %s</span>" % res.get('ds_id')]]

            for key in required_field_names:
                meta_fields = ['ds_id', 'ds_name', 'entity_short_code']
                if not key in meta_fields:
                    if key.lower().endswith(self.form_model.entity_question.code.lower()):
                        submission.append(
                            [res.get(key) + "<span class='small_grey'>  %s</span>" % res.get('entity_short_code')])
                    else:
                        submission.append(res.get(key))
            submissions.append(submission)
        return submissions


class SubmissionQuery(Query):
    def __init__(self, form_model, query_params):
        Query.__init__(self, SubmissionQueryResponseCreator(form_model), SubmissionQueryBuilder(form_model),
                       query_params)
        self.form_model = form_model

    def get_header_dict(self):
        header_dict = OrderedDict()
        self._update_static_header_info(header_dict)

        def key_attribute(field):
            return field.code.lower()

        headers = header_fields(self.form_model, key_attribute)
        for field_code,val in headers.items():
            key = es_field_name(field_code, self.form_model.id)
            if not header_dict.has_key(key): header_dict.update({key:val})

        if "reporter" in self.form_model.entity_type:
            header_dict.pop(es_field_name(self.form_model.entity_question.code, self.form_model.id))
        return header_dict

    def get_headers(self, user=None, form_code=None):
        return self.get_header_dict().keys()

    def _update_static_header_info(self, header_dict):
        header_dict.update({SubmissionIndexConstants.DATASENDER_ID_KEY: "Datasender Id"})
        header_dict.update({SubmissionIndexConstants.DATASENDER_NAME_KEY: "Datasender Name"})
        header_dict.update({"date": "Submission Date"})
        submission_type = self.query_params.get('filter')
        if not submission_type or submission_type in ["all", "deleted"]:
            header_dict.update({"status": "Status"})
        elif submission_type == 'error': \
            header_dict.update({"error_msg": "Error Message"})
        subject_title = self.form_model.entity_type[0].title()
        header_dict.update({es_field_name(self.form_model.entity_question.code,self.form_model.id): subject_title})
        header_dict.update({'entity_short_code': "%s ID" % subject_title})
        if self.form_model.event_time_question:
            header_dict.update({es_field_name(self.form_model.event_time_question.code, self.form_model.id): "Reporting Date"})


    def populate_query_options(self):
        options = super(SubmissionQuery, self).populate_query_options()
        try:
            options.update({'filter': self.query_params["filter"]})
        except KeyError:
            pass
        return options

    def query(self, database_name):
        query_all_results = self.query_builder.query_all(database_name)
        submission_headers = self.get_headers()
        query_by_submission_type = self.query_builder.filter_by_submission_type(query_all_results, self.query_params)
        filtered_query = self.query_builder.add_query_criteria(submission_headers,
                                                               self.query_params.get('search_filters').get(
                                                                   'search_text'), query_by_submission_type,
                                                               query_params=self.query_params)
        submissions = self.response_creator.create_response(submission_headers, filtered_query)
        return submissions
