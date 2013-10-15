from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.base import View
import jsonpickle
from datawinners.accountmanagement.decorators import is_not_expired, session_not_expired
from datawinners.search.entity_search import MyDataSenderQuery


class MyDataSendersAjaxView(View):
    def get(self, request, project_name, *args, **kwargs):
        search_parameters = {}
        search_text = request.GET.get('sSearch', '').strip()
        search_parameters.update({"search_text": search_text})
        search_parameters.update({"start_result_number": int(request.GET.get('iDisplayStart'))})
        search_parameters.update({"number_of_results": int(request.GET.get('iDisplayLength'))})
        search_parameters.update({"order_by": int(request.GET.get('iSortCol_0')) - 1})
        search_parameters.update({"order": "-" if request.GET.get('sSortDir_0') == "desc" else ""})

        user = request.user
        query_count, search_count, datasenders = MyDataSenderQuery().filtered_query(user, project_name,
                                                                                    search_parameters)

        return HttpResponse(
            jsonpickle.encode(
                {
                    'datasenders': datasenders,
                    'iTotalDisplayRecords': query_count,
                    'iDisplayStart': int(request.GET.get('iDisplayStart')),
                    "iTotalRecords": search_count,
                    'iDisplayLength': int(request.GET.get('iDisplayLength'))
                }, unpicklable=False), content_type='application/json')

    @method_decorator(login_required)
    @method_decorator(session_not_expired)
    @method_decorator(is_not_expired)
    def dispatch(self, *args, **kwargs):
        return super(MyDataSendersAjaxView, self).dispatch(*args, **kwargs)
