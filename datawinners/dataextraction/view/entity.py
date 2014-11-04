import json
from django.http import HttpResponse
from django_digest.decorators import httpdigest
from datawinners.dataextraction.helper import convert_date_string_to_UTC
from datawinners.main.database import get_database_manager


@httpdigest
def get_entity_actions(request, start_date=None, end_date=None):
    dbm = get_database_manager(request.user)
    start = convert_date_string_to_UTC(start_date)
    end = convert_date_string_to_UTC(end_date)

    params = {}

    if start:
        params['startkey'] = start
    if end:
        params['endkey'] = end

    rows = dbm.load_all_rows_in_view('entity_actions', **params)
    entity_actions = [{'entity_type': row["value"]['entity_type'], 'short_code': row["value"]['short_code'],
                       'date': row["value"]['created'].strftime("%Y-%m-%d %H:%M:%S")} for row in rows]

    return HttpResponse(content_type='application/json', content=json.dumps(entity_actions))