from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, F
import elasticutils

from datawinners.search.filters import SubmissionDateRangeFilter, DateQuestionRangeFilter
from datawinners.search.index_utils import es_questionnaire_field_name
from datawinners.search.query import ElasticUtilsHelper
from datawinners.search.submission_headers import HeaderFactory
from mangrove.form_model.form_model import get_form_model_by_entity_type
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT, ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT


class SubmissionSearch():
    def __init__(self, dbm, form_model, search_parameters, local_time_delta, skip_fields=[]):
        self.skip_fields = skip_fields
        self.local_time_delta = local_time_delta
        self.search_parameters = search_parameters
        self.form_model = form_model
        self.dbm = dbm

    def get_all_submissions_ids_by_criteria(self):
        total_submission_count = self.get_submission_count()
        es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
        query_fields, search = self._create_query()
        search = search.extra(size=total_submission_count, fields=[])
        body = search.to_dict()
        result = es.search(index=self.dbm.database_name, doc_type=self.form_model.id, body=body)
        return [entry['_id'] for entry in result['hits']['hits']]

    def get_facets_for_choice_fields(self):
        query_fields, search = self._create_query()
        query_body = search.to_dict()
        es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
        total_submission_count = self.get_submission_count()
        facet_results = []
        for field in self.form_model.choice_fields:
            field_name = es_questionnaire_field_name(field.code, self.form_model.id) + "_exact"
            facet = self._create_facet_request_body(field_name, query_body)
            facet_response = es.search(index=self.dbm.database_name, doc_type=self.form_model.id, body=facet,
                                       search_type='count')
            facet_result = self._get_facet_result(facet_response, field_name)
            facet_results.append(facet_result)

        return facet_results, total_submission_count

    def get_submissions_paginated(self):
        query_fields, search = self._create_query()
        search_results = search.execute()
        return search_results, query_fields

    def get_submission_count(self):
        es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
        search = Search(using=es, index=self.dbm.database_name, doc_type=self.form_model.id)
        query_fields, search = self._add_filters(search)
        body = search.to_dict()
        return \
        es.search(index=self.dbm.database_name, doc_type=self.form_model.id, body=body, search_type='count')['hits'][
            'total']

    def get_submissions_without_user_filters_count(self):
        es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
        search = Search(using=es, index=self.dbm.database_name, doc_type=self.form_model.id)
        search = self._query_by_submission_type(search)
        body = search.to_dict()
        return \
        es.search(index=self.dbm.database_name, doc_type=self.form_model.id, body=body, search_type='count')['hits'][
            'total']

    def get_scrolling_submissions_query(self):
        """
        Efficient way to fetch large number of submissions from ElasticSearch
        """
        query_fields, search = self._create_query()
        query_dict = search.to_dict()
        # if search_parameters.get('get_only_id', False):
        # query_dict["fields"] = []
        scan_response = helpers.scan(
            client=Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}]),
            index=self.dbm.database_name, doc_type=self.form_model.id,
            query=query_dict, timeout="3m", size=4000)
        return scan_response, query_fields

    def _create_facet_request_body(self, field_name, query_body):
        facet_terms = {"terms": {"field": field_name}}
        facet = {"facets": {field_name: facet_terms}}
        facet.update(query_body)
        return facet

    def _get_facet_result(self, facet_response, field_name):
        facet_result_options = []
        facet_result = {
            "es_field_name": field_name,
            "facets": facet_result_options,
            # find total submissions containing specified answer
            "total": facet_response['hits']['total'] - facet_response['facets'][field_name]['missing']
        }
        for facet in facet_response['facets'][field_name]['terms']:
            facet_result_options.append({
                "term": facet['term'],
                "count": facet['count']
            })
        return facet_result

    def _create_query(self):
        es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
        search = Search(using=es, index=self.dbm.database_name, doc_type=self.form_model.id)
        search = self._add_pagination_criteria(search)
        search = self._add_sort_criteria(search)
        search = self._add_response_fields(search)
        query_fields, search = self._add_filters(search)
        return query_fields, search

    def _add_response_fields(self, search):
        if 'response_fields' in self.search_parameters:
            search = search.fields(self.search_parameters['response_fields'])
        return search

    def _add_sort_criteria(self, search):
        if 'sort_field' not in self.search_parameters:
            return search

        order_by_field = "%s_value" % self.search_parameters["sort_field"]
        order = self.search_parameters.get("order")
        order_by_criteria = "-" + order_by_field if order == '-' else order_by_field
        return search.sort(order_by_criteria)


    def _add_pagination_criteria(self, search):
        start_result_number = self.search_parameters.get("start_result_number")
        number_of_results = self.search_parameters.get("number_of_results")
        return search.extra(from_=start_result_number, size=number_of_results)

    def _add_filters(self, search):
        search = self._query_by_submission_type(search)
        query_fields = self._get_query_fields()
        search = self._add_search_filters(search)
        return query_fields, search

    def _query_by_submission_type(self, search):
        submission_type_filter = self.search_parameters.get('filter')
        if submission_type_filter == 'deleted':
            return search.query('term', void=True)
        elif submission_type_filter == 'all':
            return search.query('term', void=False)

        if submission_type_filter == 'analysis':
            search = search.query('term', status='success')
        else:
            search = search.query('term', status=submission_type_filter)
        return search.query('term', void=False)

    def _get_query_fields(self):
        submission_type = self.search_parameters.get('filter')
        header = HeaderFactory(self.dbm, self.form_model).create_header(submission_type)
        return header.get_header_field_names()

    def _remove_hidden_fields(self, query_fields):
        if self.skip_fields:
            return [i for j, i in enumerate(query_fields) if j not in self.skip_fields]
        return query_fields

    def _add_search_filters(self, search):
        query_fields = self._get_query_fields()
        query_fields = self._remove_hidden_fields(query_fields)
        search_filter_param = self.search_parameters.get('search_filters')
        if not search_filter_param:
            return

        query_text = search_filter_param.get("search_text")
        query_text_escaped = ElasticUtilsHelper().replace_special_chars(query_text)
        if query_text:
            search = search.query("query_string", query=query_text_escaped, fields=query_fields)
        submission_date_range = search_filter_param.get("submissionDatePicker")
        submission_date_query = SubmissionDateRangeFilter(submission_date_range,
                                                          self.local_time_delta).build_filter_query()
        if submission_date_query:
            search = search.query(submission_date_query)
        search = self._add_date_range_filters(search_filter_param.get("dateQuestionFilters"), search)
        datasender_filter = search_filter_param.get("datasenderFilter")
        if datasender_filter:
            search = search.query("term",
                                  **{self.form_model.id + '_reporter.short_code.short_code_exact': datasender_filter})
        search = self._add_unique_id_filters(search_filter_param.get("uniqueIdFilters"), search)
        return search


    def _add_date_range_filters(self, date_filters, search):
        if date_filters:
            for question_code, date_range in date_filters.items():
                if date_range:
                    date_query = DateQuestionRangeFilter(date_range, self.form_model,
                                                         question_code).build_filter_query()
                    if date_query:
                        search = search.query(date_query)
        return search


    def _add_unique_id_filters(self, unique_id_filters, search):
        if unique_id_filters:
            for uniqueIdType, uniqueIdFilter in unique_id_filters.iteritems():
                entity_form_model = get_form_model_by_entity_type(self.dbm, [uniqueIdType])
                if uniqueIdFilter:
                    unique_id_filters = []

                    for question in [question for question in self.form_model.entity_questions if
                                     question.unique_id_type == uniqueIdType]:
                        es_field_code = es_questionnaire_field_name(question.code, self.form_model.id,
                                                                    parent_field_code=question.parent_field_code) + \
                                        "." + entity_form_model.id + "_q6" + "." + entity_form_model.id + "_q6" + "_exact"
                        # es_field_code = es_unique_id_code_field_name(
                        # es_questionnaire_field_name(question.code, form_model.id, parent_field_code=question.parent_field_code)) + "_exact"
                        unique_id_filters.append(F("term", **{es_field_code: uniqueIdFilter}))
                    search = search.filter(F('or', unique_id_filters))
        return search


    def _query_for_questionnaire(self):
        return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(
            self.dbm.database_name).doctypes(self.form_model.id)






