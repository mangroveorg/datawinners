# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os

from django.conf import settings
from django.utils.translation import ugettext as _, ugettext_lazy
from datawinners.entity.player import FormCodeDoesNotMatchException
from datawinners.entity.player_factory import FilePlayerFactory

from datawinners.entity.entity_exceptions import InvalidFileFormatException
from mangrove.errors.MangroveException import CSVParserInvalidHeaderFormatException, XlsParserInvalidHeaderFormatException
from datawinners.utils import get_organization

#TODO This is a hack. To be fixed after release. Introduce handlers and get error objects from mangrove
from mangrove.transport.player.parser import XlsDatasenderParser, XlsOrderedParser


def _tabulate_failures(rows):
    tabulated_data = []
    for row in rows:
        row[1].errors['row_num'] = row[0] + 2

        if isinstance(row[1].errors['error'], dict):
            errors = ''
            for key, value in row[1].errors['error'].items():
                if 'is required' in value:
                    code = value.split(' ')[3]
                    errors = errors + "\n" + _('Answer for question %s is required') % (code, )
                elif 'xx.xxxx yy.yyyy' in value:
                    errors = errors + "\n" + _(
                        'Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315')
                elif 'longer' in value:
                    text = value.split(' ')[1]
                    errors = errors + "\n" + _("Answer %s for question %s is longer than allowed.") % (text, key)
                elif 'must be between' in value:
                    text = value.split(' ')[2]
                    low = value.split(' ')[6]
                    high = value.split(' ')[8]
                    errors = errors + "\n" + _("The answer %s must be between %s and %s") % (text, low, high)
                else:
                    errors = errors + "<br>" + _(value)
        else:
            errors = _(row[1].errors['error'])

        row[1].errors['error'] = errors.lstrip("<br>")
        tabulated_data.append(row[1].errors)
    return tabulated_data

def _tabulate_success(success_responses):
    tabulated_data = []
    for success_response in success_responses:
        tabulated_data.append(success_response.processed_data)
    return tabulated_data

def _get_player(default_parser, extension, form_code, manager):
    return FilePlayerFactory().create(manager, extension, default_parser, form_code)


def _handle_uploaded_file(file_name, file, manager, default_parser=None, form_code=None):
    base_name, extension = os.path.splitext(file_name)
    player = _get_player(default_parser, extension, form_code, manager)
    responses = player.accept(file)
    return responses


def _get_imported_entities(responses):
    short_codes = dict()
    datarecords_id = []
    form_code = []
    for response in responses:
        if response.success:
            short_codes.update({response.short_code: response.entity_type[0]})
            datarecords_id.append(response.datarecord_id)
            if response.form_code not in form_code:
                form_code.append(response.form_code)
    return {"short_codes": short_codes, "datarecords_id": datarecords_id, "form_code": form_code}


def _get_failed_responses(responses):
    return [i for i in enumerate(responses) if not i[1].success]


def _get_successful_responses(responses):
    return [response for response in responses if response.success]


def import_datasenders(request, manager):
    error_message = None
    failure_imports = None
    successful_imports = None
    try:
        #IE sends the file in request.FILES['qqfile'] whereas all other browsers in request.GET['qqfile']. The following flow handles that flow.
        file_name, file = _file_and_name(request) if 'qqfile' in request.GET else _file_and_name_for_ie(request)
        responses = _handle_uploaded_file(file_name=file_name, file=file, manager=manager,
                                          default_parser=XlsDatasenderParser, form_code=None)
        failures = _get_failed_responses(responses)
        successes = _get_successful_responses(responses)
        total = len(failures) + len(successes)
        if total == 0:
            error_message = _("The imported file is empty.")
        failure_imports = _tabulate_failures(failures)
        successful_imports = _tabulate_success(successes)
    except CSVParserInvalidHeaderFormatException or XlsParserInvalidHeaderFormatException as e:
        error_message = e.message
    except InvalidFileFormatException:
        error_message = _(u"We could not import your data ! You are using a document format we canʼt import. Please use the import template file!")
    except FormCodeDoesNotMatchException as e:
        error_message = e.message
    except Exception:
        error_message = _(u"Some unexpected error happened. Please check the excel file and import again.")
    return error_message, failure_imports, successful_imports


def import_subjects(request, manager, form_code):
    response_message = ''
    error_message = None
    failure_imports = None
    successful_imports = None
    imported_entities = {}
    try:
        #IE sends the file in request.FILES['qqfile'] whereas all other browsers in request.GET['qqfile']. The following flow handles that flow.
        file_name, file = _file_and_name(request) if 'qqfile' in request.GET else _file_and_name_for_ie(request)
        responses = _handle_uploaded_file(file_name=file_name, file=file, manager=manager,
                                          default_parser=XlsOrderedParser, form_code=form_code)
        imported_entities = _get_imported_entities(responses)
        form_code = imported_entities.get("form_code")[0] if len(imported_entities.get("form_code")) == 1 else None

        if form_code is not None and \
                len(imported_entities.get("datarecords_id")) and settings.CRS_ORG_ID == get_organization(
                request).org_id:
            from django.core.management import call_command

            datarecords_id = imported_entities.get("datarecords_id")
            call_command('crs_datamigration', form_code, *datarecords_id)

        imported_entities = imported_entities.get("short_codes")
        successful_import_count = len(imported_entities)
        total = len(responses)
        if total == 0:
            error_message = _("The imported file is empty.")
        failures = _get_failed_responses(responses)
        successes = _get_successful_responses(responses)
        failure_imports = _tabulate_failures(failures)
        successful_imports = _tabulate_success(successes)
        response_message = ugettext_lazy('%s of %s records uploaded') % (successful_import_count, total)
    except CSVParserInvalidHeaderFormatException or XlsParserInvalidHeaderFormatException as e:
        error_message = e.message
    except InvalidFileFormatException:
        error_message = _(
            u"We could not import your data ! You are using a document format we canʼt import. Please use the import template file!")
    except FormCodeDoesNotMatchException as e:
        error_message = e.message
    except Exception:
        error_message = _(u"Some unexpected error happened. Please check the excel file and import again.")
        if settings.DEBUG:
            raise
    return error_message, failure_imports, response_message, imported_entities, successful_imports


def _file_and_name_for_ie(request):
    file_name = request.FILES.get('qqfile').name
    file = request.FILES.get('qqfile').read()
    return file_name, file


def _file_and_name(request):
    file_name = request.GET.get('qqfile')
    file = request.raw_post_data
    return file_name, file
