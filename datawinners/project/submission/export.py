from django.http import HttpResponse
from datawinners import utils
from django.template.defaultfilters import slugify


def create_excel_response(headers, raw_data_list, file_name):
    response = HttpResponse(mimetype="application/vnd.ms-excel")
    response['Content-Disposition'] = 'attachment; filename="%s.xls"' % (slugify(file_name),)

    wb = utils.get_excel_sheet([headers] + raw_data_list, 'data_log')
    wb.save(response)

    return response

def export_filename(submission_type, project_name):
    suffix = submission_type + '_log' if submission_type else 'analysis'
    file_name = "%s_%s" % (project_name, suffix)
    return file_name