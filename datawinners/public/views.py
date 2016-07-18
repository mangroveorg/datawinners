from django.shortcuts import render_to_response
from django.template import RequestContext

from datawinners.entity.geo_data import geo_json
from datawinners.main.database import get_db_manager
from mangrove.datastore.entity_share import get_entity_preference_by_share_token
from mangrove.form_model.form_model import get_form_model_by_entity_type


def render_map(request, share_token):
    entity_preference = get_entity_preference_by_share_token(get_db_manager("public"), share_token)
    dbm = get_db_manager(entity_preference.org_id)
    form_model = get_form_model_by_entity_type(dbm, [entity_preference.entity_type.lower()])
    return render_to_response(
        'map.html',
        {
            "entity_type": entity_preference.entity_type,
            "filters": _get_filters(form_model, entity_preference.filters),
            "geo_json": geo_json(dbm, entity_preference.entity_type, request.GET),
            "is_public": True
        },
        context_instance=RequestContext(request)
    )


def _get_filters(form_model, filters):
    filters = [
        {'code': field['code'], 'label': field['label'], 'choices': field['choices']}
        for field in form_model.form_fields if field['code'] in filters
    ]
    return filters
