import json
from django.http import HttpResponse
from django.views.generic.base import View
import elasticutils
from datawinners.main.utils import get_database_name
from datawinners.settings import ELASTIC_SEARCH_URL


class AllDataSenderAutoCompleteView(View):
    def get(self, request):
        search_text = request.GET["term"]
        database_name = get_database_name(request.user)
        f = elasticutils.F(name=search_text) | elasticutils.F(short_code=search_text)
        query = elasticutils.S().es(urls=ELASTIC_SEARCH_URL).indexes(database_name).doctypes("reporter").filter(f).values_dict()
        resp = [{"id": r["short_code"], "label":r["name"]} for r in query]
        return HttpResponse(json.dumps(resp))