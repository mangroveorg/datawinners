import StringIO
import elasticutils
from pyes import ES
import pyes
from pyes.filters import BoolFilter, TermFilter
from pyes.query import FilteredQuery, BoolQuery, TermQuery, QueryStringQuery, MatchAllQuery

from datawinners.search.filters import SubmissionDateRangeFilter, DateQuestionRangeFilter
from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.query import ElasticUtilsHelper
from datawinners.search.submission_headers import HeaderFactory
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT


def _add_sort_criteria(search_parameters):
    order_by_criteria = "%s_value" % search_parameters["sort_field"]
    order = search_parameters.get("order")
    if order == '-':
        return order_by_criteria + ":desc"
    return order_by_criteria


def _add_pagination_criteria(search_parameters):
    start_result_number = search_parameters.get("start_result_number")
    number_of_results = search_parameters.get("number_of_results")
    return {'start': start_result_number, 'size': number_of_results}


def _query_by_submission_type(submission_type_filter, queries):
    if submission_type_filter == 'deleted':
        queries.append(TermQuery(field='void', value=True))
        return
    elif submission_type_filter == 'all':
        queries.append(TermQuery(field='void', value=False))
        return
    elif submission_type_filter == 'analysis':
        queries.append(TermQuery(field='status', value='success'))
    else:
        queries.append(TermQuery(field='status', value=submission_type_filter))
    queries.append(TermQuery(field='void', value=False))


def _get_query_fields(form_model, submission_type):
    header = HeaderFactory(form_model).create_header(submission_type)
    return header.get_header_field_names()


def _add_date_range_filters(date_filters, form_model, queries):
    if date_filters:
        for question_code, date_range in date_filters.items():
            if date_range:
                date_query = DateQuestionRangeFilter(date_range, form_model, question_code).build_filter_query()
                if date_query:
                    queries.append(date_query)


def _add_unique_id_filters(form_model, queries, uniqueIdFilters):
    if uniqueIdFilters:
        for uniqueIdType, uniqueIdFilter in uniqueIdFilters.iteritems():
            if uniqueIdFilter:
                for question in [question for question in form_model.entity_questions if
                                 question.unique_id_type == uniqueIdType]:
                    es_field_code = es_unique_id_code_field_name(
                        es_questionnaire_field_name(question.code, form_model.id)) + "_exact"
                    queries.append(TermQuery(field=es_field_code, value=uniqueIdFilter))


def _add_search_filters(search_filter_param, form_model, local_time_delta, query_fields, queries):
    if not search_filter_param:
        return

    query_text = search_filter_param.get("search_text")
    query_text_escaped = ElasticUtilsHelper().replace_special_chars(query_text)
    if query_text:
        queries.append(QueryStringQuery(query=query_text_escaped, search_fields=query_fields))
    submission_date_range = search_filter_param.get("submissionDatePicker")
    submission_date_query = SubmissionDateRangeFilter(submission_date_range, local_time_delta).build_filter_query()
    if submission_date_query:
        queries.append(submission_date_query)
    _add_date_range_filters(search_filter_param.get("dateQuestionFilters"), form_model, queries)
    datasender_filter = search_filter_param.get("datasenderFilter")
    if datasender_filter:
        queries.append(TermQuery(field='ds_id_exact', value=datasender_filter))
    _add_unique_id_filters(form_model, queries, search_filter_param.get("uniqueIdFilters"))


def _add_filters(form_model, search_parameters, local_time_delta):
    queries = []
    _query_by_submission_type(search_parameters.get('filter'), queries)
    query_fields = _get_query_fields(form_model, search_parameters.get('filter'))
    _add_search_filters(search_parameters.get('search_filters'), form_model, local_time_delta, query_fields, queries)
    return query_fields, queries


def _query_for_questionnaire(dbm, form_model):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(
        dbm.database_name).doctypes(form_model.id)


def get_submission_search_query(dbm, form_model, search_parameters, local_time_delta):
    conn = ES(timeout=ELASTIC_SEARCH_TIMEOUT)
    paginated_parameters = _add_pagination_criteria(search_parameters)
    query_fields, filters = _add_filters(form_model, search_parameters, local_time_delta)
    filtered_query = BoolQuery(must=filters)
    sort_criteria = _add_sort_criteria(search_parameters)
    search_results = conn.search(indices=[dbm.database_name], doc_types=[form_model.id],
                                            query=filtered_query, sort=sort_criteria, **paginated_parameters)
    return search_results, query_fields


def get_all_submission_count(dbm, form_model, search_parameters):
    conn = ES(timeout=ELASTIC_SEARCH_TIMEOUT)
    paginated_parameters = _add_pagination_criteria(search_parameters)
    submission_count = conn.count(indices=[dbm.database_name], doc_types=[form_model.id], query=MatchAllQuery())
    return submission_count



def get_all_submissions_ids_by_criteria(dbm, form_model, search_parameters, local_time_delta):
    query = _query_for_questionnaire(dbm, form_model)
    query = query[:query.count()]
    query_fields, query_with_search_filters = _add_filters(form_model, query, search_parameters, local_time_delta)
    return [entry._id for entry in query_with_search_filters.values_dict('void')]

