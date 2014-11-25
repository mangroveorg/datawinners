import elasticutils

from datawinners.search.filters import SubmissionDateRangeFilter, DateQuestionRangeFilter
from datawinners.search.index_utils import es_unique_id_code_field_name, es_questionnaire_field_name
from datawinners.search.query import ElasticUtilsHelper
from datawinners.search.submission_headers import HeaderFactory
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT


def _add_sort_criteria(query, search_parameters):
    order = search_parameters.get("order")
    sort_field = search_parameters.get("sort_field")
    query = query.order_by(order + sort_field + "_value")
    return query


def _add_pagination_criteria(query, search_parameters):
    start_result_number = search_parameters.get("start_result_number")
    number_of_results = search_parameters.get("number_of_results")
    return query[start_result_number:start_result_number + number_of_results]

def _filter_by_submission_type( query, submission_type_filter):
        if submission_type_filter == 'deleted':
            return query.filter(void=True)
        elif submission_type_filter == 'all':
            return query.filter(void=False)
        elif submission_type_filter == 'analysis':
            query = query.filter(status="success")
        else:
            query = query.filter(status=submission_type_filter)
        return query.filter(void=False)


def _get_query_fields(form_model, submission_type):
    header = HeaderFactory(form_model).create_header(submission_type)
    return header.get_header_field_names()

def _add_date_range_filters(query, date_filters, form_model):
    if date_filters:
        for question_code, date_range in date_filters.items():
            if date_range:
                query = DateQuestionRangeFilter(date_range, form_model, question_code).build_filter_query(query)
    return query

def _add_unique_id_filters(form_model, query, uniqueIdFilters):
    if uniqueIdFilters:
        for uniqueIdType, uniqueIdFilter in uniqueIdFilters.iteritems():
            if uniqueIdFilter:
                search_options = elasticutils.F()
                for question in [question for question in form_model.entity_questions if
                                 question.unique_id_type == uniqueIdType]:
                    es_field_code = es_unique_id_code_field_name(
                        es_questionnaire_field_name(question.code, form_model.id))
                    search_options |= elasticutils.F(**{es_field_code: uniqueIdFilter})
                query = query.filter(search_options)
    return query


def _add_search_filters(query, search_filter_param, form_model, local_time_delta):
    if search_filter_param:
        submission_date_range = search_filter_param.get("submissionDatePicker")
        query = SubmissionDateRangeFilter(submission_date_range, local_time_delta).build_filter_query(query)
        query = _add_date_range_filters(query, search_filter_param.get("dateQuestionFilters"), form_model)
        datasender_filter = search_filter_param.get("datasenderFilter")
        if datasender_filter:
            query = query.filter(ds_id=datasender_filter)
        query = _add_unique_id_filters(form_model, query, search_filter_param.get("uniqueIdFilters"))
    return query


def _add_filters(form_model, paginated_query, search_parameters, local_time_delta):
    query = _filter_by_submission_type(paginated_query, search_parameters.get('filter'))
    query_fields = _get_query_fields(form_model, search_parameters.get('filter'))
    query_text = search_parameters.get("search_text")
    query = ElasticUtilsHelper().add_free_text_search_criteria(query, query_fields, query_text)
    query_with_search_filters = _add_search_filters(query, search_parameters.get('search_filters'), form_model, local_time_delta)
    return query_fields, query_with_search_filters


def _query_for_questionnaire(dbm, form_model):
    return elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(
        dbm.database_name).doctypes(form_model.id)


def get_submission_search_query(dbm, form_model, search_parameters, local_time_delta):
    query = _query_for_questionnaire(dbm, form_model)
    query = _add_sort_criteria(query, search_parameters)
    paginated_query = _add_pagination_criteria(query, search_parameters)
    query_fields, query_with_search_filters = _add_filters(form_model, paginated_query, search_parameters, local_time_delta)
    return paginated_query, query_with_search_filters, query_fields

def get_all_submissions_ids_by_criteria(dbm, form_model, search_parameters, local_time_delta):
    query = _query_for_questionnaire(dbm, form_model)
    query = query[:query.count()]
    query_with_search_filters = _add_search_filters(query, search_parameters.get('search_filters'), form_model, local_time_delta)
    return [entry._id for entry in query_with_search_filters.values_dict('void')]

