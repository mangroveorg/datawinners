import json
from string import lower
from django.http import HttpResponse
from django.views.generic.base import View
import elasticutils
from datawinners.main.utils import get_database_name
from datawinners.settings import ELASTIC_SEARCH_URL


class AllDataSenderAutoCompleteView(View):
    def get(self, request):
        search_text = lower(request.GET["term"] or "")
        database_name = get_database_name(request.user)
        query = elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes("reporter") \
            .query(or_={'name__match': search_text, 'name_value': search_text, 'short_code__match': search_text,
                        'short_code_value': search_text}) \
            .values_dict()
        resp = [{"id": r["short_code"], "label": r["name"]} for r in query[:min(query.count(), 50)]]
        return HttpResponse(json.dumps(resp))
