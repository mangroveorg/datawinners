# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
from datawinners import settings
from datawinners.main.utils import get_database_manager, is_reporter
from datawinners.entity.entity_exceptions import InvalidFileFormatException
from mangrove.datastore.entity import get_all_entities
from mangrove.errors.MangroveException import CSVParserInvalidHeaderFormatException, XlsParserInvalidHeaderFormatException
from mangrove.form_model.form_model import NAME_FIELD, MOBILE_NUMBER_FIELD, DESCRIPTION_FIELD
from mangrove.transport.player.parser import CsvParser, XlsParser
from mangrove.transport.player.player import CsvPlayer, XlsPlayer
from mangrove.utils.types import sequence_to_str

def tabulate_failures(rows):
    tabulated_data = []
    for row in rows:
        errors = ''
        row[1].errors['row_num'] = row[0] + 2
        if type(row[1].errors['error']) is list:
            for error in row[1].errors['error']:
                errors = errors + ' ' + error
            row[1].errors['error'] = errors
        tabulated_data.append(row[1].errors)
    return tabulated_data


def _format(value):
    return value if value else "--"


def _tabulate_data(entity):
    id = entity.id
    geocode = entity.geometry.get('coordinates')
    geocode_string = ", ".join([str(i) for i in geocode]) if geocode is not None else "--"
    location = _format(sequence_to_str(entity.location_path))
    name = _format(entity.value(NAME_FIELD))
    mobile_number = _format(entity.value(MOBILE_NUMBER_FIELD))
    description = _format(entity.value(DESCRIPTION_FIELD))
    return dict(id=id, name=name, short_name=entity.short_code, type=".".join(entity.type_path), geocode=geocode_string, location=location,
                description=description, mobile_number=mobile_number)


def _get_entity_type_from_row(row):
    type = row['doc']['aggregation_paths']['_type']
    return type

def _is_not_reporter(entity):
    return not is_reporter(entity)

def load_subject_registration_data(manager, filter_entities = _is_not_reporter):
    entities = get_all_entities(dbm=manager, include_docs=True)
    data = []
    for entity in entities:
        if filter_entities(entity):
            data.append(_tabulate_data(entity))
    return data


def load_all_subjects(request):
    manager = get_database_manager(request.user)
    return load_subject_registration_data(manager)


def load_all_subjects_of_type(manager, filter_entities = is_reporter):
    return load_subject_registration_data(manager, filter_entities)

def _handle_uploaded_file(file_name,file,manager):
    base_name, extension = os.path.splitext(file_name)
    if extension == '.csv':
        csv_player = CsvPlayer(dbm=manager, parser=CsvParser())
        response = csv_player.accept(file)
    elif extension == '.xls':
        xls_player = XlsPlayer(dbm=manager, parser=XlsParser())
        response = xls_player.accept(file)
    else:
        raise InvalidFileFormatException()
    return response


def import_data(request,manager):
    success = False
    response_message = ''
    error_message = None
    failure_imports = None
    try:
        file_name = request.GET.get('qqfile')
        response = _handle_uploaded_file(file_name=file_name,file=request.raw_post_data,manager=manager)
        successful_imports = len([index for index in response if index.success])
        total = len(response)
        failure = [i for i in enumerate(response) if not i[1].success]
        failure_imports = tabulate_failures(failure)
        if total == successful_imports:
            success = True
        response_message = '%s of %s records uploaded' % (successful_imports, total)
    except CSVParserInvalidHeaderFormatException or XlsParserInvalidHeaderFormatException as e:
        error_message = e.message
    except InvalidFileFormatException:
        error_message = 'We could not import your data ! \
                        You are using a document format we canʼt import. Please use a Comma Separated Values (.csv) or a Excel (.xls) file!'
    except Exception:
        error_message = 'Some unexpected error happened. Please check the CSV file and import again.'
        if settings.DEBUG:
            raise
    return error_message, failure_imports, success, response_message