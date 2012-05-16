# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from collections import OrderedDict
from copy import copy
from mangrove.datastore.documents import attributes
from mangrove.datastore.entity_type import get_all_entity_types
import os
from django.conf import settings
from datawinners.location.LocationTree import get_location_tree
from datawinners.main.utils import  include_of_type, exclude_of_type
from datawinners.entity.entity_exceptions import InvalidFileFormatException
from mangrove.datastore.entity import get_all_entities
from mangrove.errors.MangroveException import MangroveException, DataObjectAlreadyExists
from mangrove.errors.MangroveException import CSVParserInvalidHeaderFormatException, XlsParserInvalidHeaderFormatException
from mangrove.form_model.form_model import    REPORTER, get_form_model_by_code, get_form_model_by_entity_type
from mangrove.transport.player.parser import CsvParser, XlsOrderedParser, XlsParser
from mangrove.transport import Channel, TransportInfo, Response
from mangrove.transport.player.player import Player
from mangrove.utils.types import   is_sequence
from mangrove.datastore import entity
from mangrove.transport.facade import RegistrationWorkFlow, GeneralWorkFlow, ActivityReportWorkFlow
from django.utils.translation import ugettext as _, ugettext_lazy, ugettext

from datawinners.location.LocationTree import get_location_hierarchy
from datawinners.submission.location import LocationBridge
from mangrove.contrib.registration_validators import case_insensitive_lookup
from datawinners.accountmanagement.helper import get_all_registered_phone_numbers_on_trial_account
from mangrove.form_model.form_model import ENTITY_TYPE_FIELD_CODE, MOBILE_NUMBER_FIELD_CODE

class FilePlayer(Player):
    def __init__(self, dbm, parser, channel_name, location_tree=None):
        Player.__init__(self, dbm, location_tree)
        self.parser = parser
        self.channel_name = channel_name

    @classmethod
    def build(cls, manager, extension, location_tree, form_code=None):
        if extension == '.csv':
            parser = CsvParser()
            channel = Channel.CSV
        elif extension == '.xls':
            parser = XlsParser() if form_code is None else XlsOrderedParser(form_code)
            channel = Channel.XLS
        else:
            raise InvalidFileFormatException()
        return FilePlayer(manager, parser, channel, location_tree=LocationBridge(get_location_tree(), get_loc_hierarchy=get_location_hierarchy))

    def _process(self,form_code, values):
        form_model = get_form_model_by_code(self.dbm, form_code)
        values = GeneralWorkFlow().process(values)
        if form_model.is_registration_form():
            values = RegistrationWorkFlow(self.dbm, form_model, self.location_tree).process(values)
        if form_model.entity_defaults_to_reporter():
            reporter_entity = entity.get_by_short_code(self.dbm, values.get(form_model.entity_question.code.lower()), form_model.entity_type)
            values = ActivityReportWorkFlow(form_model, reporter_entity).process(values)
        return form_model, values

    def accept(self, file_contents):
        responses = []
        from datawinners.utils import get_organization_from_manager
        organization = get_organization_from_manager(self.dbm)
        registered_phone_numbers = get_all_registered_phone_numbers_on_trial_account() \
            if organization.in_trial_mode else []
        submissions = self.parser.parse(file_contents)
        for (form_code, values) in submissions:
            transport_info = TransportInfo(transport=self.channel_name, source=self.channel_name, destination="")
            submission = self._create_submission(transport_info, form_code, copy(values))
            try:
                form_model, values = self._process(form_code, values)
                if case_insensitive_lookup(values, ENTITY_TYPE_FIELD_CODE) == REPORTER:
                    phone_number = case_insensitive_lookup(values, MOBILE_NUMBER_FIELD_CODE)
                    if phone_number in registered_phone_numbers:
                        raise DataObjectAlreadyExists(_("Data Sender"), _("Mobile Number"), phone_number)
                response = self.submit(form_model, values, submission, [])
                if not response.success:
                    response.errors = dict(error=response.errors, row=values)
                responses.append(response)
            except DataObjectAlreadyExists as e:
                response = Response(reporters=[], submission_id=None)
                response.success = False
                message = ugettext("%s with %s = %s already exists.")
                response.errors = dict(error=message % (e.data[2], e.data[0], e.data[1]), row=values)
                responses.append(response)
            except MangroveException as e:
                response = Response(reporters=[], submission_id=None)
                response.success = False
                response.errors = dict(error=e.message, row=values)
                responses.append(response)
        return responses

#TODO This is a hack. To be fixed after release. Introduce handlers and get error objects from mangrove
def tabulate_failures(rows):
    tabulated_data = []
    for row in rows:
        row[1].errors['row_num'] = row[0] + 2

        if isinstance(row[1].errors['error'], dict):
            errors = ''
            for key,value in row[1].errors['error'].items():
                if 'is required' in value:
                    code = value.split(' ')[3]
                    errors = errors + "\n" + _('Answer for question %s is required')% (code, )
                elif 'xx.xxxx yy.yyyy' in value:
                    errors = errors + "\n" + _('Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315')
                elif 'longer' in value:
                    text = value.split(' ')[1]
                    errors = errors + "\n" + _("Answer %s for question %s is longer than allowed.") % (text, key)
                elif 'must be between' in value:
                    text = value.split(' ')[2]
                    low = value.split(' ')[6]
                    high = value.split(' ')[8]
                    errors = errors + "\n" + _("The answer %s must be between %s and %s") % (text, low, high)
                else:
                    errors = errors + "\n" +_(value)
        else:
            errors = _(row[1].errors['error'])

        row[1].errors['error'] = errors
        tabulated_data.append(row[1].errors)
    return tabulated_data


def _tabulate_data(entity, form_model, values_for_fields):
    data = {'id': entity.id, 'short_code': entity.short_code}

    dict = OrderedDict()
    tuples = [(field.code, field.name) for field in form_model.fields]
    for (code, name) in tuples :
        if name in entity.data.keys():
            dict[code] = _get_field_value(name, entity)
        else:
            dict[code] = _get_field_default_value(name, entity)

    stringified_dict = form_model.stringify(dict)

    dict_values = [stringified_dict[field] for field in values_for_fields]
    data['cols'] = dict_values
    return data


def _get_entity_type_from_row(row):
    type = row['doc']['aggregation_paths']['_type']
    return type


def load_subject_registration_data(manager,
                                   filter_entities=exclude_of_type,
                                   type=REPORTER, tabulate_function=_tabulate_data):
    if type==REPORTER :
        form_model = get_form_model_by_code(manager, 'reg')
    else:
        form_model = get_form_model_by_entity_type(manager, _entity_type_as_sequence(type))

    fields, labels, codes = get_entity_type_fields(manager, type)
    entities = get_all_entities(dbm=manager)
    data = []
    for entity in entities:
        if filter_entities(entity, type):
            data.append(tabulate_function(entity, form_model, codes))
    return data, fields, labels


def _get_entity_types(manager):
    entity_types = get_all_entity_types(manager)
    entity_list = [entity[0] for entity in entity_types if entity[0] != 'reporter']
    entity_list.sort()
    return entity_list


def _get_registration_form_models(manager):
    subjects = {}
    form_models = manager.load_all_rows_in_view('questionnaire')
    for form_model in form_models:
        if form_model.value['is_registration_model'] and form_model.value['name'] != 'Reporter':
            subjects[form_model.value['entity_type'][0]] = form_model
    return subjects


def get_field_infos(fields,langauge='en'):
    fields_names = []
    labels = []
    codes = []
    for field in fields:
        if field['name'] != 'entity_type':
            fields_names.append(field['name'])
            labels.append(field['label'][langauge])
            codes.append(field['code'])
    return fields_names, labels, codes


def get_entity_type_infos(entity, form_model=None, manager=None):
    if form_model is None:
        if entity == 'reporter' :
            form_code = 'reg'
        else:
            form_model = get_form_model_by_entity_type(manager, _entity_type_as_sequence(entity))
            form_code = form_model.form_code
        form_model = manager.load_all_rows_in_view("questionnaire", key=form_code)[0]
    names, labels, codes = get_field_infos(form_model.value['json_fields'],form_model.value['metadata'][attributes.ACTIVE_LANGUAGES][0])
    subject = dict(entity = entity,
        code = form_model.value["form_code"],
        names = names,
        labels = labels,
        codes = codes,
        data = [],
    )
    return subject


def load_all_subjects(manager):
    entity_types_names = _get_entity_types(manager)
    subjects = _get_registration_form_models(manager)

    subjects_list = {}
    for entity in entity_types_names:
        if entity in subjects.keys():
            form_model_row = subjects[entity]
        else:
            form_model_row = subjects['registration']
        subjects_list[entity] = get_entity_type_infos(entity, form_model_row)

    entities = get_all_entities(dbm=manager)
    for entity in entities:
        if exclude_of_type(entity, REPORTER):
            entity_type = entity.type_string
            if entity_type in subjects_list.keys():
                form_model = get_form_model_by_code(manager, subjects_list[entity_type]['code'])
                subjects_list[entity_type]['data'].append(_tabulate_data(entity, form_model, subjects_list[entity_type]['codes']))

    data = [subjects_list[entity] for entity in entity_types_names]
    return data


def load_all_subjects_of_type(manager, filter_entities=include_of_type, type=REPORTER):
    return load_subject_registration_data(manager, filter_entities, type)


def _handle_uploaded_file(file_name, file, manager, form_code=None):
    base_name, extension = os.path.splitext(file_name)
    player = FilePlayer.build(manager, extension, get_location_tree(), form_code)
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
        form_code = request.GET.get("form_code", None)
        responses = _handle_uploaded_file(file_name=file_name, file=file, manager=manager, form_code=form_code)
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


def _entity_type_as_sequence(entity_type):
    if not is_sequence(entity_type):
        entity_type = [entity_type.lower()]
    return entity_type


def get_entity_type_fields(manager, type=REPORTER):
    form_model = get_form_model_by_entity_type(manager, _entity_type_as_sequence(type))
    form_code = "reg"
    if form_model is not None:
        form_code = form_model.form_code
    form_model_rows = manager.load_all_rows_in_view("questionnaire", key=form_code)
    fields, labels, codes = get_field_infos(form_model_rows[0].value['json_fields'],form_model_rows[0].value['metadata'][attributes.ACTIVE_LANGUAGES][0])
    return fields, labels, codes


def _get_field_value(key, entity):
    value = entity.value(key)
    if key == 'geo_code':
        if value is None:
            return entity.geometry.get('coordinates')
    elif key == 'location':
        if value is None:
            return entity.location_path

    return value

def _get_field_default_value(key, entity):
    if key == 'geo_code':
        return entity.geometry.get('coordinates')
    if key == 'location':
        return  entity.location_path
    if key == 'short_code':
        return entity.short_code
    return None