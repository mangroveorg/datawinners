from django.db.models import Q
from datawinners.common.constant import ADMIN_QUERY, ADMIN_ORDER_TYPE, ADMIN_ORDER_COLUMN, ADMIN_PAGINATION


def get_admin_panel_filter(getRequestParameters):
    textSearchFilter = {}
    for key in getRequestParameters.keys():
        if key == ADMIN_QUERY or key == ADMIN_ORDER_TYPE or key == ADMIN_ORDER_COLUMN or key == ADMIN_PAGINATION:
            pass
        else:
            textSearchFilter[key] = getRequestParameters[key]
    return textSearchFilter

def get_text_search_filter(getRequestParameters, searchFields):
    textSearchFilter = Q()
    if ADMIN_QUERY in getRequestParameters:
        for search_field in searchFields:
            text_search_value = getRequestParameters[ADMIN_QUERY]
            textSearchFilter = textSearchFilter | Q(**{search_field + "__contains": text_search_value})
    return textSearchFilter
