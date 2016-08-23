from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from datawinners.entity.geo_data import geo_jsons
from datawinners.feature_toggle.models import FeatureSubscription, Feature
from datawinners.main.database import get_db_manager
from mangrove.datastore.entity_share import get_entity_preference_by_share_token
from mangrove.form_model.form_model import get_form_model_by_entity_type

from datawinners.utils import get_mapbox_api_key


def render_map(request, share_token):
    entity_preference = get_entity_preference_by_share_token(get_db_manager("public"), share_token)
    dbm = get_db_manager(entity_preference.org_id)

    if not _flag_active("idnr_map", entity_preference.org_id.split('_')[-1].upper()):
        raise Http404

    form_model = get_form_model_by_entity_type(dbm, [entity_preference.entity_type.lower()])

    return render_to_response(
        'map.html',
        {
            "entity_type": entity_preference.entity_type,
            "filters": _get_filters(form_model, entity_preference.filters),
            "geo_jsons": geo_jsons(dbm, entity_preference.entity_type, request.GET, entity_preference.details, entity_preference.specials),
            "fallback_location": entity_preference.fallback_location,
            "mapbox_api_key": get_mapbox_api_key(request.META['HTTP_HOST'])
        },
        context_instance=RequestContext(request)
    )


def _get_filters(form_model, filters):
    filters = [
        {'code': field['code'], 'label': field['label'], 'choices': field['choices']}
        for field in form_model.form_fields if field['code'] in filters
    ]
    return filters

def _flag_active(flag, org_id):
    feature = Feature.objects.get(name=flag)
    fs = FeatureSubscription.objects.get(feature=feature)
    organizations = fs.organizations.filter(org_id=org_id)
    return len(organizations) > 0
