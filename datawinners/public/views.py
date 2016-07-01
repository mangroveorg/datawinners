from django.shortcuts import render_to_response
from django.template import RequestContext

from datawinners.entity.geo_data import geo_json
from datawinners.main.database import get_db_manager
from mangrove.datastore.entity_share import get_entity_preference_by_share_token


def render_map(request, share_token):
    entity_preference = get_entity_preference_by_share_token(get_db_manager("public"), share_token)
    entity_type = entity_preference.entity_type
    dbm = get_db_manager(entity_preference.org_id)
    return render_to_response('map.html',
                              {'entity_type': entity_type, "geo_json": geo_json(dbm, entity_type)},
                              context_instance=RequestContext(request))
