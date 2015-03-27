from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q

from datawinners.search.query import ElasticUtilsHelper
from mangrove.form_model.project import get_entity_type_fields


REPORTER_DOC_TYPE = 'reporter'

def _add_pagination_criteria(search_parameters, search):
    start_result_number = search_parameters.get("start_result_number")
    number_of_results = search_parameters.get("number_of_results")
    return search.extra(from_=start_result_number, size=number_of_results)


def _add_response_fields(search_parameters, search):
    if 'response_fields' in search_parameters:
        search = search.fields(search_parameters['response_fields'])
    return search


def _add_sort_criteria(search_parameters, search):
    if 'sort_field' not in search_parameters:
        return search

    order_by_field = "%s_value" % search_parameters["sort_field"]
    order = search_parameters.get("order")
    order_by_criteria = "-" + order_by_field if order == '-' else order_by_field
    return search.sort(order_by_criteria)


def _get_query_fields(dbm):
    fields, old_labels, codes = get_entity_type_fields(dbm)
    fields.append("devices")
    fields.append('projects')
    # fields.append('groups')
    return fields


def _add_project_query(search, search_filter_param):
    project_name = search_filter_param.get('project_name')
    if project_name:
        search = search.query("term", projects_value=project_name.lower())
    projects_name = search_filter_param.get('projects')
    if projects_name:
        search = search.query("terms", projects_value=projects_name)
    return search


def _add_group_query(search, search_filter_param):
    group_name = search_filter_param.get('group_name')
    if group_name:
        search = search.query("term", customgroups_value=group_name.lower())
    return search


def _add_free_text_search_query(query_fields, search, search_filter_param):
    query_text = search_filter_param.get("search_text")
    if query_text:
        query_text_escaped = ElasticUtilsHelper().replace_special_chars(query_text)
        search = search.query("query_string", query=query_text_escaped, fields=query_fields)
    return search


def _restrict_test_ds_query(search):
    search = search.query(~Q('term', short_code_value='test'))
    return search


def _add_non_deleted_ds_query(search):
    search = search.query('term', void=False)
    return search


def _add_search_filters(search_filter_param, query_fields, search):
    search = _restrict_test_ds_query(search)
    search = _add_non_deleted_ds_query(search)
    if not search_filter_param:
        return search
    search = _add_free_text_search_query(query_fields, search, search_filter_param)
    search = _add_group_query(search, search_filter_param)
    search = _add_project_query(search, search_filter_param)

    return search


def _add_filters(dbm, search_parameters, search):
    query_fields = _get_query_fields(dbm)
    search = _add_search_filters(search_parameters.get('search_filters'), query_fields,
                                 search)
    return query_fields, search


def get_data_sender_without_search_filters_count(dbm, search_parameters):
    es = Elasticsearch()
    search = Search(using=es, index=dbm.database_name, doc_type=REPORTER_DOC_TYPE)
    search_filter_param = search_parameters.get('search_filters', {})
    search = _add_group_query(search, search_filter_param)
    search = _restrict_test_ds_query(search)
    search = _add_project_query(search, search_filter_param)
    search = _add_non_deleted_ds_query(search)
    body = search.to_dict()
    return es.search(index=dbm.database_name, doc_type=REPORTER_DOC_TYPE, body=body, search_type='count')['hits']['total']


def get_data_sender_count(dbm, search_parameters):
    es = Elasticsearch()
    search = Search(using=es, index=dbm.database_name, doc_type=REPORTER_DOC_TYPE)
    query_fields, search = _add_filters(dbm, search_parameters, search)
    body = search.to_dict()
    return es.search(index=dbm.database_name, doc_type=REPORTER_DOC_TYPE, body=body, search_type='count')['hits']['total']


def get_data_sender_search_results(dbm, search_parameters):
    es = Elasticsearch()
    search = Search(using=es, index=dbm.database_name, doc_type=REPORTER_DOC_TYPE)
    search = _add_pagination_criteria(search_parameters, search)
    search = _add_sort_criteria(search_parameters, search)
    search = _add_response_fields(search_parameters, search)
    query_fields, search = _add_filters(dbm, search_parameters, search)
    datasenders = search.execute()
    return query_fields, datasenders


def get_all_datasenders_search_results(dbm, search_parameters):
    required_count = get_data_sender_count(dbm, search_parameters)
    search_parameters["number_of_results"] = required_count
    search_parameters["start_result_number"] = 0
    fields, search_results = get_data_sender_search_results(dbm, search_parameters)
    return search_results