import json

from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from datawinners.entity.geo_data import geo_jsons
from datawinners.feature_toggle.models import FeatureSubscription, Feature
from datawinners.main.database import get_db_manager
from datawinners.utils import get_mapbox_api_key, is_json
from mangrove.datastore.entity_share import get_entity_preference_by_share_token
from mangrove.form_model.field import UniqueIdUIField, UniqueIdField, TextField
from mangrove.form_model.form_model import get_form_model_by_entity_type


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


def _get_filters(form_model, filters, remove_options = None):
    filters = [{'code': field.code, 'label': field.label, 'choices': field.options if remove_options == None else filter(lambda fo: fo['text'] not in remove_options, field.options)}
               for field in form_model.fields if field.code in filters and not isinstance(field, UniqueIdField) and hasattr(field,'options')]

    return filters





def _get_uniqueid_filters(form_model, filters, dbm, remove_options = None):
    uniqueid_filters = []
    multi_filters = [json.loads(f.replace("'", '"')) for f in filters if is_json(f.replace("'", '"'))]
    single_filters = [f for f in filters if not is_json(f.replace("'", '"'))]
    d = dict((field.code, field) for field in form_model.fields)

    uniqueid_filters += [
        {
            'code': d[f].code, 'label': d[f].label,
            'choices': UniqueIdUIField(d[f], dbm).options
        }
        for f in single_filters if isinstance(d[f], UniqueIdField)
    ]


    # for textfield filter

    for f in single_filters:
        if isinstance(d[f], TextField):
            map_function = """
            function(doc) {
                    if (doc.document_type == "Entity" && !doc.void && doc.aggregation_paths['_type'][0] == '%s') {
                        emit(doc.data['%s'].value.toUpperCase(),doc.data['%s'].value.toUpperCase());
                    }
                }
            """
            map_function = map_function % (form_model.entity_type[0], d[f].name, d[f].name)
            reduce_function = """
                function(keys, values) {
                  return true
                }
            """
            
            list_options = [(row.key, row.key) for row in dbm.database.query(map_function, reduce_function, group=True)]


            uniqueid_filters += [
                {
                    'code': d[f].code, 'label': d[f].label,
                    'choices': list_options if remove_options == None else filter(lambda lo: lo[0] not in remove_options, list_options)
                }

            ]
    """
    uniqueid_filters += [
        {
            'code': ",".join(mf),
            'label': d[mf[0]].unique_id_type.capitalize(),
            'choices': list(set(reduce(lambda prev, f: prev + UniqueIdUIField(d[f], dbm).options, mf, [])))
        }
        for mf in multi_filters
    ]
    """


    uniqueid_filters = []
    for mf in multi_filters:
        list_options = list(set(reduce(lambda prev, f: prev + UniqueIdUIField(d[f], dbm).options, mf, [])))
        uniqueid_filters.append({
            'code': ",".join(mf),
            'label': d[mf[0]].unique_id_type.capitalize(),
            'choices': list_options if remove_options == None else filter(lambda lo: lo[1] not in remove_options, list_options)
        })


    


    return filter(None, uniqueid_filters)


def _flag_active(flag, org_id):
    feature = Feature.objects.get(name=flag)
    fs = FeatureSubscription.objects.get(feature=feature)
    organizations = fs.organizations.filter(org_id=org_id)
    return len(organizations) > 0
