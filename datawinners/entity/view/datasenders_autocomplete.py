import json
from string import lower
from django.http import HttpResponse
from django.views.generic.base import View
import elasticutils
from datawinners.main.utils import get_database_name
from datawinners.settings import ELASTIC_SEARCH_URL, ELASTIC_SEARCH_TIMEOUT


class AllDataSenderAutoCompleteView(View):
    def get(self, request):
        search_text = lower(request.GET["term"] or "")
        database_name = get_database_name(request.user)
        query = elasticutils.S().es(urls=ELASTIC_SEARCH_URL, timeout=ELASTIC_SEARCH_TIMEOUT).indexes(database_name).doctypes("reporter") \
            .query(or_={'name__match': search_text, 'name_value': search_text, 'short_code__match': search_text,
                        'short_code_value': search_text}) \
            .values_dict()
        resp = [{"id": r["short_code"], "label": self.get_label(r)} for r in query[:min(query.count(), 50)]]
        return HttpResponse(json.dumps(resp))

    def get_label(self, r):
        if r['name']:
            return r['name']
        return r['mobile_number']