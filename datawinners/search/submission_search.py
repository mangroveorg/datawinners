from collections import OrderedDict
from babel.dates import format_datetime
import datetime
import elasticutils
# from datawinners import search
from datawinners.search.filters import SubmissionDateRangeFilter, ReportingDateRangeFilter
from mangrove.form_model.field import DateField
from datawinners.settings import ELASTIC_SEARCH_URL
from mangrove.form_model.form_model import header_fields
from datawinners.search.query import QueryBuilder, Query
from datawinners.search import filters


class SubmissionIndexConstants:
    DATASENDER_ID_KEY = "ds_id"
    DATASENDER_NAME_KEY = "ds_name"


class SubmissionQueryBuilder(QueryBuilder):
    def __init__(self, form_model=None):
        QueryBuilder.__init__(self)
        self.form_model = form_model

    def create_query(self, database_name, *doc_type):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes(*doc_type)

    def create_paginated_query(self, query, query_params):
        query = super(SubmissionQueryBuilder, self).create_paginated_query(query, query_params)

        submission_type_filter = query_params.get('filter')
        if submission_type_filter:
            if submission_type_filter == 'deleted':
                return query.filter(void=True)
            query = (query.filter(status=submission_type_filter))
        return query.filter(void=False)

    def add_query_criteria(self, query_fields, query_text, query, query_params=None):
        query = super(SubmissionQueryBuilder, self).add_query_criteria(query_fields, query_text, query, query_params)
        search_filter_param = query_params.get('search_filters')
        if search_filter_param:
            submission_date_range = search_filter_param.get("submissionDatePicker")
            reporting_date_range = search_filter_param.get("reportingPeriodPicker")
            datasender_filter = search_filter_param.get("datasenderFilter")
            query = SubmissionDateRangeFilter(submission_date_range).build_filter_query(query)
            query = ReportingDateRangeFilter(reporting_date_range, self.form_model).build_filter_query(query)
            if datasender_filter:
                query = query.filter(ds_id=datasender_filter)
        return query

    def query_all(self, database_name, **kwargs):
        query = self.create_query(database_name, database_name)
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
                    if key.lower() == self.form_model.entity_question.code.lower():
                        submission.append(
                            [res.get(key) + "<span class='small_grey'>  %s</span>" % res.get('entity_short_code')])
                    elif isinstance(res.get(key), dict):
                        submission.append(res.get(key).values())
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
            return self._field_code_in_lowercase(field)

        header_fields(self.form_model, key_attribute, header_dict)
        if "reporter" in self.form_model.entity_type:
            header_dict.pop(self.form_model.entity_question.code)
        return header_dict

    def get_headers(self, user, form_code):
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
        header_dict.update({self._field_code_in_lowercase(self.form_model.entity_question): subject_title})
        header_dict.update({'entity_short_code': "%s ID" % subject_title})
        if self.form_model.event_time_question:
            header_dict.update({self._field_code_in_lowercase(self.form_model.event_time_question): "Reporting Date"})

    def _field_code_in_lowercase(self, field):
        return field.code.lower()


    def populate_query_options(self):
        options = super(SubmissionQuery, self).populate_query_options()
        try:
            options.update({'filter': self.query_params["filter"]})
        except KeyError:
            pass
        return options


