# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from copy import copy
from mangrove.transport.facade import RegistrationWorkFlow
from mangrove.transport.submissions import Submission
import os
from django.conf import settings
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import get_database_manager, include_of_type, exclude_of_type
from datawinners.entity.entity_exceptions import InvalidFileFormatException
from mangrove.datastore.entity import get_all_entities
from mangrove.errors.MangroveException import MangroveException, DataObjectAlreadyExists, MultipleReportersForANumberException
from mangrove.errors.MangroveException import CSVParserInvalidHeaderFormatException, XlsParserInvalidHeaderFormatException
from mangrove.form_model.form_model import NAME_FIELD, MOBILE_NUMBER_FIELD, DESCRIPTION_FIELD, REPORTER, get_form_model_by_code
from mangrove.transport.player.parser import CsvParser, XlsParser
from mangrove.transport import Channel, TransportInfo, Response
from mangrove.transport.player.player import Player
from mangrove.utils.types import sequence_to_str
from django.utils.translation import ugettext as _, ugettext_lazy, ugettext

#TODO This class has been moved because it was not possible to do internationalization with Mangrove swallowing exceptions
from datawinners.location.LocationTree import get_location_hierarchy

class FilePlayer(Player):
    def __init__(self, dbm, parser, channel_name, location_tree=None, get_location_hierarchy=None):
        Player.__init__(self, dbm, location_tree, get_location_hierarchy)
        self.parser = parser
        self.channel_name = channel_name

    @classmethod
    def build(cls, manager, extension, location_tree):
        if extension == '.csv':
            parser = CsvParser()
            channel = Channel.CSV
        elif extension == '.xls':
            parser = XlsParser()
            channel = Channel.XLS
        else:
            raise InvalidFileFormatException()
        return FilePlayer(manager, parser, channel, location_tree, get_location_hierarchy)

    def accept(self, file_contents):
        responses = []
        submissions = self.parser.parse(file_contents)
        for (form_code, values) in submissions:
            transport_info = TransportInfo(transport=self.channel_name, source=self.channel_name, destination="")
            submission = Submission(self.dbm, transport_info, form_code, copy(values))
            submission.save()
            try:
                form_model = get_form_model_by_code(self.dbm, form_code)
                if form_model.is_registration_form():
                    values = RegistrationWorkFlow(self.dbm, form_model, self.location_tree, self.get_location_hierarchy).process(values)
                form_submission = self.submit(form_model, values)
                submission.update(form_submission.saved, form_submission.errors, form_submission.data_record_id,
                                  form_submission.form_model.is_in_test_mode())
                response = Response(reporters=[], submission_id=submission.uuid, form_submission=form_submission)
                if not form_submission.saved:
                    response.errors = dict(error=form_submission.errors, row=values)
                responses.append(response)
            except DataObjectAlreadyExists as e:
                response = Response(reporters=[], submission_id=None, form_submission=None)
                response.success = False
                message = ugettext("%s with %s = %s already exists.")
                response.errors = dict(error=message % (e.data[2], e.data[0], e.data[1]), row=values)
                responses.append(response)
            except MultipleReportersForANumberException as e:
                response = Response(reporters=[], submission_id=None, form_submission=None)
                response.success = False
                message = ugettext("Sorry, the telephone number %s has already been registered")
                response.errors = dict(error=message % e.data[0], row=values)
                responses.append(response)
            except MangroveException as e:
                response = Response(reporters=[], submission_id=None, form_submission=None)
                response.success = False
                response.errors = dict(error=e.message, row=values)
                responses.append(response)
        return responses

#TODO This method is a proof that Exceptions needs to be handled by the client application
def tabulate_failures(rows):
    tabulated_data = []
    for row in rows:
        row[1].errors['row_num'] = row[0] + 2

        if isinstance(row[1].errors['error'], dict):
            errors = ''
            for key,value in row[1].errors['error'].items():
                if key == 'n' or key == 't':
                    code = value.split(' ')[3]
                    errors = errors + _('Answer for question %s is required')% (code, )
                if key == 's':
                    errors = errors + value
                if key == 'g':
                    if 'xx.xxxx yy.yyyy' in value:
                        errors = errors + _('Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx yy.yyyy. Example -18.8665 47.5315')
                    else:
                        text = value.split(' ')[2]
                        low = value.split(' ')[6]
                        high = value.split(' ')[8]
                        errors = errors + _("The answer %s must be between %s and %s") % (text, low, high)
                if key == 'm':
                    if 'is required' in value:
                        code = value.split(' ')[3]
                        errors = errors + _('Answer for question %s is required')% (code, )
                    if 'longer' in value:
                        text = value.split(' ')[1]
                        errors = errors + _("Answer %s for question %s is longer than allowed.") % (text, key)
                    else:
                        errors = errors + _(value)
        else:
            errors = _(row[1].errors['error'])

        row[1].errors['error'] = errors
        tabulated_data.append(row[1].errors)
    return tabulated_data


def _format(value):
    return value if value is not None else "--"


def _tabulate_data(entity):
    id = entity.id
    geocode = entity.geometry.get('coordinates')
    geocode_string = ", ".join([str(i) for i in geocode]) if geocode is not None else "--"
    location = _format(sequence_to_str(entity.location_path, u", "))
    name = _format(entity.value(NAME_FIELD))
    mobile_number = _format(entity.value(MOBILE_NUMBER_FIELD))
    description = _format(entity.value(DESCRIPTION_FIELD))
    return dict(id=id, name=name, short_name=entity.short_code, type=".".join(entity.type_path), geocode=geocode_string,
                location=location,
                description=description, mobile_number=mobile_number)


def _get_entity_type_from_row(row):
    type = row['doc']['aggregation_paths']['_type']
    return type


def load_subject_registration_data(manager, filter_entities=exclude_of_type,type=REPORTER):
    entities = get_all_entities(dbm=manager)
    data = []
    for entity in entities:
        if filter_entities(entity,type):
            data.append(_tabulate_data(entity))
    return data


def load_all_subjects(request):
    manager = get_database_manager(request.user)
    return load_subject_registration_data(manager)


def load_all_subjects_of_type(manager, filter_entities=include_of_type,type=REPORTER):
    return load_subject_registration_data(manager, filter_entities,type)


def _handle_uploaded_file(file_name, file, manager):
    base_name, extension = os.path.splitext(file_name)
    player = FilePlayer.build(manager, extension, get_location_tree())
    response = player.accept(file)
    return response


def _get_imported_entities(responses):
    imported_entities = {response.short_code: response.entity_type[0] for response in responses if response.success}
    return imported_entities


def _get_failed_responses(responses):
    return [i for i in enumerate(responses) if not i[1].success]


def _get_success_status(successful_imports, total):
    return True if total == successful_imports else False


def import_data(request, manager):
    response_message = ''
    error_message = None
    failure_imports = None
    imported_entities = {}
    try:
        #IE sends the file in request.FILES['qqfile'] whereas all other browsers in request.GET['qqfile']. The following flow handles that flow.
        file_name, file = _file_and_name(request) if 'qqfile' in request.GET else _file_and_name_for_ie(request)
        responses = _handle_uploaded_file(file_name=file_name, file=file, manager=manager)
        imported_entities = _get_imported_entities(responses)
        successful_imports = len(imported_entities)
        total = len(responses)
        failures = _get_failed_responses(responses)
        failure_imports = tabulate_failures(failures)
        response_message = ugettext_lazy('%s of %s records uploaded') % (successful_imports, total)
    except CSVParserInvalidHeaderFormatException or XlsParserInvalidHeaderFormatException as e:
        error_message = e.message
    except InvalidFileFormatException:
        error_message = _(u"We could not import your data ! You are using a document format we canʼt import. Please use a Comma Separated Values (.csv) or a Excel (.xls) file!")
    except Exception:
        error_message = 'Some unexpected error happened. Please check the CSV file and import again.'
        if settings.DEBUG:
            raise
    return error_message, failure_imports, response_message, imported_entities

def _file_and_name_for_ie(request):
    file_name = request.FILES.get('qqfile').name
    file = request.FILES.get('qqfile').read()
    return file_name, file

def _file_and_name(request):
    file_name = request.GET.get('qqfile')
    file = request.raw_post_data
    return file_name, file