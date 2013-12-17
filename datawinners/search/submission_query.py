import elasticutils
from datawinners.search.filters import SubmissionDateRangeFilter, ReportingDateRangeFilter
from datawinners.search.submission_headers import HeaderFactory
from datawinners.settings import ELASTIC_SEARCH_URL
from datawinners.search.query import QueryBuilder, Query


class SubmissionQueryBuilder(QueryBuilder):
    def __init__(self, form_model=None):
        QueryBuilder.__init__(self)
        self.form_model = form_model

    def create_query(self, database_name, *doc_type):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes(*doc_type)

    def filter_by_submission_type(self, query, query_params):
        submission_type_filter = query_params.get('filter')
        if submission_type_filter == 'deleted':
            return query.filter(void=True)
        elif submission_type_filter == 'all':
            return query.filter(void=False)
        elif submission_type_filter == 'analysis':
            query = query.filter(status="success")
        else:
            query = query.filter(status=submission_type_filter)
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
                query = query.filter(entity_short_code=subjectFilter)
        return query

    def query_all(self, database_name, *args, **kwargs):
        query = self.create_query(database_name, *args)
        query_all_results = query[:query.count()]
        return query_all_results.filter(**kwargs)


class SubmissionQueryResponseCreator():
    def __init__(self, form_model):
        self.form_model = form_model

    def create_response(self, required_field_names, query):
        submissions = []
        for res in query.values_dict(tuple(required_field_names)):
            submission = [res._id]
            submission.append(
                ["%s<span class='small_grey'>  %s</span>" % (res.get('ds_name'), res.get('ds_id'))]) if res.get(
                'ds_name') else submission.append(res.get('ds_name'))

            for key in required_field_names:
                meta_fields = ['ds_id', 'ds_name', 'entity_short_code']
                if not key in meta_fields:
                    if key.lower().endswith(self.form_model.entity_question.code.lower()):
                        submission.append(
                            ["%s<span class='small_grey'>  %s</span>" % (
                                res.get(key), res.get('entity_short_code'))] if res.get(key) else res.get(key))
                    else:
                        submission.append(res.get(key))
            submissions.append(submission)
        return submissions


class SubmissionQuery(Query):
    def __init__(self, form_model, query_params):
        Query.__init__(self, SubmissionQueryResponseCreator(form_model), SubmissionQueryBuilder(form_model),
                       query_params)
        self.form_model = form_model

    def get_headers(self, user, entity_type):
        submission_type = self.query_params.get('filter')
        return HeaderFactory(self.form_model).get_header(submission_type)

    def populate_query_options(self):
        options = super(SubmissionQuery, self).populate_query_options()
        try:
            options.update({'filter': self.query_params["filter"]})
        except KeyError:
            pass
        return options

    def query(self, database_name):
        query_all_results = self.query_builder.query_all(database_name)
        submission_type = self.query_params.get('filter')

        submission_headers = HeaderFactory(self.form_model).get_header(submission_type)
        query_by_submission_type = self.query_builder.filter_by_submission_type(query_all_results, self.query_params)
        filtered_query = self.query_builder.add_query_criteria(submission_headers,
                                                               self.query_params.get('search_filters').get(
                                                                   'search_text'), query_by_submission_type,
                                                               query_params=self.query_params)
        submissions = self.response_creator.create_response(submission_headers, filtered_query)
        return submissions


