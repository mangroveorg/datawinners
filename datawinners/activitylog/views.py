from django.contrib.auth.decorators import login_required
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired
from django.views.decorators.csrf import csrf_exempt
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from datawinners.activitylog.forms import LogFilterForm
from datawinners.activitylog.models import UserActivityLog
from datawinners.utils import convert_dmy_to_ymd, get_organization
from datetime import date
from mangrove.utils.json_codecs import encode_json
from django.utils.translation import ugettext


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
@is_datasender
def show_log(request):
    org_id = get_organization(request).org_id
    args = dict(organization=org_id)
    if request.method == 'GET':
        form = LogFilterForm(request=request)
    else:
        form = LogFilterForm(request.POST, request=request)
        filter = form.data.copy()
        filter.pop("csrfmiddlewaretoken")
        for key,value in filter.items():
            if value != "":
                if key == "daterange":
                    dates = value.split(" %s " % ugettext("to"))
                    args["log_date__gte"] = convert_dmy_to_ymd(dates[0])
                    try:
                        end_date = date.today()
                        if len(dates) > 1:
                            end_date = convert_dmy_to_ymd(dates[1])
                        else:
                            end_date = convert_dmy_to_ymd(dates[0])
                    except KeyError:
                        pass
                    args["log_date__lte"] = "%s 23:59:59" % end_date
                    continue
                args[key] = value
    log_data = UserActivityLog.objects.select_related().filter(**args).order_by("-log_date")

    return render_to_response("activitylog/activitylog.html",
                              {
                                'form': form,
                                'log_data': repr(encode_json([log.to_render() for log in log_data]))
                              },
                              context_instance=RequestContext(request))