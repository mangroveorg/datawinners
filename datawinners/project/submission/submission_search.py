from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, Q, F
import elasticutils
from datawinners.search.filters import SubmissionDateRangeFilter, DateQuestionRangeFilter
from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.query import ElasticUtilsHelper
from datawinners.search.submission_headers import HeaderFactory
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT, ELASTIC_SEARCH_HOST, ELASTIC_SEARCH_PORT
import logging
from elasticsearch_dsl.aggs import A

logger = logging.getLogger("datawinners")


def _add_sort_criteria(search_parameters, search):
    if 'sort_field' not in search_parameters:
        return search

    order_by_field = "%s_value" % search_parameters["sort_field"]
    order = search_parameters.get("order")
    order_by_criteria = "-" + order_by_field if order == '-' else order_by_field
    return search.sort(order_by_criteria)


def _add_pagination_criteria(search_parameters, search):
    start_result_number = search_parameters.get("start_result_number")
    number_of_results = search_parameters.get("number_of_results")
    return search.extra(from_=start_result_number, size=number_of_results)


def _aggregate_other_duplicates(form_model, search_parameters, search):
    if search_parameters == 'datasender':
        a = A("terms", field='ds_id_exact', size=0, min_doc_count=2)
        b = A("top_hits", size=(2**20))
        search.aggs.bucket('tag', a).bucket('tag', b)
    return search


def _aggregate_exact_match_duplicates(form_model, search):
    search = search.params(search_type="count")
    nested_search = search
    for index, field in enumerate(form_model.form_fields):
        field_name = es_questionnaire_field_name(field['code'], form_model.id)
        field_suffix = '_value' if field['type'] == 'date' else '_exact'
        if index == 0:
            nested_search.aggs.bucket('tag', 'terms', field=field_name+field_suffix, size=0, min_doc_count=2)
        else:
            nested_search.bucket('tag', 'terms', field=field_name+field_suffix, size=0, min_doc_count=2)
        nested_search = nested_search.aggs['tag']
    nested_search.bucket('tag', 'terms', field='status_exact', size=0, min_doc_count=2)\
        .bucket('tag', 'terms', field='ds_id_exact', size=0, min_doc_count=2)\
        .bucket('tag', 'top_hits')

    return search


def _query_by_submission_type(form_model, submission_type_filter, search):
    if submission_type_filter == 'duplicates':
        return _aggregate_exact_match_duplicates(form_model, search)

    if submission_type_filter == 'deleted':
        return search.query('term', void=True)
    elif submission_type_filter == 'all' or submission_type_filter == 'duplicates':
        return search.query('term', void=False)

    if submission_type_filter == 'analysis':
        search = search.query('match', status='Success')
    else:
        search = search.query('term', status=submission_type_filter)
    return search.query('term', void=False)


def _get_query_fields(form_model, submission_type):
    header = HeaderFactory(form_model).create_header(submission_type)
    return header.get_header_field_names()


def _add_date_range_filters(date_filters, form_model, search):
    if date_filters:
        for question_code, date_range in date_filters.items():
            if date_range:
                date_query = DateQuestionRangeFilter(date_range, form_model, question_code).build_filter_query()
                if date_query:
                    search = search.query(date_query)
    return search


def _add_unique_id_filters(form_model, unique_id_filters, search):
    if unique_id_filters:
        for uniqueIdType, uniqueIdFilter in unique_id_filters.iteritems():
            if uniqueIdFilter:
                unique_id_filters = []

                for question in [question for question in form_model.entity_questions if
                                 question.unique_id_type == uniqueIdType]:
                    es_field_code = es_unique_id_code_field_name(
                        es_questionnaire_field_name(question.code, form_model.id, parent_field_code=question.parent_field_code)) + "_exact"
                    unique_id_filters.append(F("term", **{es_field_code: uniqueIdFilter}))
                search = search.filter(F('or', unique_id_filters))
    return search


def _add_search_filters(search_filter_param, form_model, local_time_delta, query_fields, search):
    if not search_filter_param:
        return

    query_text = search_filter_param.get("search_text")
    query_text_escaped = ElasticUtilsHelper().replace_special_chars(query_text)
    if query_text:
        search = search.query("query_string", query=query_text_escaped)
    submission_date_range = search_filter_param.get("submissionDatePicker")
    submission_date_query = SubmissionDateRangeFilter(submission_date_range, local_time_delta).build_filter_query()
    if submission_date_query:
        search = search.query(submission_date_query)
    search = _add_date_range_filters(search_filter_param.get("dateQuestionFilters"), form_model, search)
    datasender_filter = search_filter_param.get("datasenderFilter")
    if datasender_filter:
        search = search.query("term", ds_id_exact=datasender_filter)
    search = _add_unique_id_filters(form_model, search_filter_param.get("uniqueIdFilters"), search)
    return search


def _add_filters(form_model, search_parameters, local_time_delta, search):
    search = _query_by_submission_type(form_model, search_parameters.get('filter'), search)
    query_fields = _get_query_fields(form_model, search_parameters.get('filter'))
    search = _add_search_filters(search_parameters.get('search_filters'), form_model, local_time_delta, query_fields,
                                 search)
    return query_fields, search


def _query_for_questionnaire(dbm, form_model):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(
        dbm.database_name).doctypes(form_model.id)


def _add_response_fields(search_parameters, search):
    if 'response_fields' in search_parameters and len(search_parameters['response_fields']) > 0:
        search = search.fields(search_parameters['response_fields'])
    return search


def _create_query(dbm, form_model, local_time_delta, search_parameters):
    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
    search = Search(using=es, index=dbm.database_name, doc_type=form_model.id)
    search = _add_pagination_criteria(search_parameters, search)
    search = _add_sort_criteria(search_parameters, search)
    search = _add_response_fields(search_parameters, search)
    query_fields, search = _add_filters(form_model, search_parameters, local_time_delta, search)
    return query_fields, search


def get_submissions_paginated(dbm, form_model, search_parameters, local_time_delta):
    query_fields, search = _create_query(dbm, form_model, local_time_delta, search_parameters)
    if search_parameters.get('filter') == 'duplicates':
        search = _aggregate_other_duplicates(form_model, search_parameters.get('search_filters').get('duplicatesForFilter'), search)
    search_results = search.execute()
    return search_results, query_fields


def _create_search(dbm, form_model, local_time_delta, pagination_params, sort_params, search_parameters):
    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
    search = Search(using=es, index=dbm.database_name, doc_type=form_model.id)
    search = search.sort(sort_params)
    search = search.extra(**pagination_params)
    search = search.query('match', status='Success')
    search = search.query('term', void=False)
    if search_parameters.get('data_sender_filter'):
        search = search.query(
                              "term",
                              **{"datasender.id": search_parameters.get('data_sender_filter')})
    if search_parameters.get('unique_id_filters'):
        search = _add_unique_id_filters(form_model, search_parameters.get('unique_id_filters'), search)
    if search_parameters.get('date_question_filters'):
        for key, values in search_parameters.get('date_question_filters').iteritems():
            query = DateQuestionRangeFilter(values['dateRange'], form_model, key).build_filter_query()
            if query is not None:
                search = search.query(query)
    if search_parameters.get('search_text'):
        query_text_escaped = ElasticUtilsHelper().replace_special_chars(search_parameters.get('search_text'))
        search = search.query("query_string", query=query_text_escaped)
    submission_date_query = SubmissionDateRangeFilter(search_parameters.get('submission_date_range'), local_time_delta).build_filter_query()
    if submission_date_query:
        search = search.query(submission_date_query)
    return search


def get_submissions_paginated_simple(dbm, form_model, pagination_params, local_time_delta, sort_params=None, search_parameters={}):
    search = _create_search(dbm, form_model, local_time_delta, pagination_params, sort_params, search_parameters)
    search_results = None
    try:
        search_results = search.execute()
    except:
        logger.exception('Exception happened while fetching analysis data')
    return search_results


def get_scrolling_submissions_query(dbm, form_model, search_parameters, local_time_delta):
    """
    Efficient way to fetch large number of submissions from ElasticSearch
    """
    query_fields, search = _create_query(dbm, form_model, local_time_delta, search_parameters)
    query_dict = search.to_dict()
    # if search_parameters.get('get_only_id', False):
    #     query_dict["fields"] = []
    scan_response = helpers.scan(client=Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}]), index=dbm.database_name, doc_type=form_model.id,
                                 query=query_dict, timeout="3m", size=4000)
    return scan_response, query_fields


def get_submissions_without_user_filters_count(dbm, form_model, search_parameters):
    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
    search = Search(using=es, index=dbm.database_name, doc_type=form_model.id)
    search = _query_by_submission_type(form_model, search_parameters.get('filter'), search)
    body = search.to_dict()
    return es.search(index=dbm.database_name, doc_type=form_model.id, body=body, search_type='count')['hits']['total']


def get_submission_count(dbm, form_model, search_parameters, local_time_delta):
    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
    search = Search(using=es, index=dbm.database_name, doc_type=form_model.id)
    query_fields, search = _add_filters(form_model, search_parameters, local_time_delta, search)
    body = search.to_dict()
    return es.search(index=dbm.database_name, doc_type=form_model.id, body=body, search_type='count')['hits']['total']


def _create_facet_request_body(field_name, query_body):
    facet_terms = {"terms": {"field": field_name}}
    facet = {"facets": {field_name: facet_terms}}
    facet.update(query_body)
    return facet


def _get_aggregation_result(field_name, search_results):
    agg_result = search_results.aggregations[field_name]
    agg_result_options = []
    for bucket in agg_result.buckets:
        agg_result_options.append({
            "term": bucket['key'],
            "count": bucket['doc_count']
        })
    agg_result = {
        "es_field_name": field_name,
        "facets": agg_result_options,
        # find total submissions containing specified answer
        "total": search_results.hits.total
    }
    return agg_result


def get_aggregations_for_choice_fields(dbm, form_model,
                                       local_time_delta, pagination_params,
                                       sort_params, search_parameters):
    search = _create_search(dbm, form_model, local_time_delta,
                            pagination_params, sort_params,
                            search_parameters)
    search = search.params(search_type="count")
    field_names = []
    for field in form_model.choice_fields:
        field_name = es_questionnaire_field_name(field.code, form_model.id)
        a = A("terms", field=field_name+'_exact', size=0)
        search.aggs.bucket(field_name, a)
        field_names.append(field_name)
    search_results = search.execute()
    aggs_results = [_get_aggregation_result(field_name, search_results)
                    for field_name in field_names]
    return aggs_results, search_results.hits.total


def get_all_submissions_ids_by_criteria(dbm, form_model, search_parameters, local_time_delta):
    total_submission_count = get_submission_count(dbm, form_model, search_parameters, local_time_delta)
    es = Elasticsearch(hosts=[{"host": ELASTIC_SEARCH_HOST, "port": ELASTIC_SEARCH_PORT}])
    query_fields, search = _create_query(dbm, form_model, local_time_delta, search_parameters)
    search = search.extra(size=total_submission_count, fields=[])
    body = search.to_dict()
    result = es.search(index=dbm.database_name, doc_type=form_model.id, body=body)
    return [entry['_id'] for entry in result['hits']['hits']]

