import json
from django.contrib.auth.decorators import login_required
from datawinners.accountmanagement.decorators import is_datasender, session_not_expired, is_not_expired
from django.views.decorators.csrf import csrf_exempt
from django.template.context import RequestContext
from django.shortcuts import render_to_response
from datawinners.accountmanagement.localized_time import get_country_time_delta, convert_utc_to_localized, \
    convert_local_to_utc
from datawinners.activitylog.forms import LogFilterForm
from datawinners.activitylog.models import UserActivityLog
from datawinners.utils import convert_dmy_to_ymd, get_organization
from datetime import date, datetime, timedelta
from mangrove.utils.json_codecs import encode_json
from django.utils.translation import ugettext

def convert_to_ymd(date):
    return datetime.strftime(date, "%Y-%m-%d")


@login_required
@session_not_expired
@csrf_exempt
@is_not_expired
@is_datasender
def show_log(request):
    organization = get_organization(request)
    org_id = organization.org_id
    args = dict(organization=org_id)
    time_delta = get_country_time_delta(organization.country)
    if request.method == 'GET':
        form = LogFilterForm(request=request)
    else:
        form = LogFilterForm(request.POST, request=request)
        filter = form.data.copy()
        filter.pop("csrfmiddlewaretoken")
        for key, value in filter.items():
            if value != "":
                if key == "daterange":
                    dates = value.split(" %s " % ugettext("to"))
                    # args["log_date__gte"] = convert_dmy_to_ymd(dates[0])
                    args["log_date__gte"] = convert_local_to_utc(dates[0] + " 00:00:00", time_delta, "%d-%m-%Y %H:%M:%S")
                    try:
                        end_date = date.today()
                        if len(dates) > 1:
                            # end_date = convert_dmy_to_ymd(dates[1])
                            end_date = convert_local_to_utc(dates[1] + " 23:59:59", time_delta, "%d-%m-%Y %H:%M:%S")
                        else:
                            end_date = convert_local_to_utc(dates[0] + " 23:59:59", time_delta, "%d-%m-%Y %H:%M:%S")
                    except KeyError:
                        pass
                    args["log_date__lte"] = "%s" % end_date
                    continue
                args[key] = value
    log_data = UserActivityLog.objects.select_related().filter(**args).order_by("-log_date")
    for entry in log_data:
        entry.log_date = convert_utc_to_localized(time_delta, entry.log_date)
    return render_to_response("activitylog/activitylog.html",
                              {
                                'form': form,
                                'log_data': repr(encode_json([log.to_render() for log in log_data]))
                              },
                              context_instance=RequestContext(request))