# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import os
from datawinners import settings
from datawinners.main.utils import get_database_manager
from datawinners.entity.entity_exceptions import InvalidFileFormatException
from mangrove.datastore.entity import get_all_entities, get_by_short_code
from mangrove.errors.MangroveException import CSVParserInvalidHeaderFormatException, XlsParserInvalidHeaderFormatException
from mangrove.form_model.form_model import NAME_FIELD, MOBILE_NUMBER_FIELD, DESCRIPTION_FIELD
from mangrove.transport.player.player import CsvPlayer, CsvParser, XlsPlayer, XlsParser
from mangrove.transport.submissions import SubmissionHandler
from mangrove.utils.types import sequence_to_str

def tabulate_failures(rows):
    tabulated_data = []
    errors = ''
    for row in rows:
        row[1].errors['row_num'] = row[0] + 2
        if type(row[1].errors['error']) is list:
            for error in row[1].errors['error']:
                errors = errors + ' ' + error
            row[1].errors['error'] = errors
        tabulated_data.append(row[1].errors)
    return tabulated_data


def _tabulate_data(entity, row, short_code, type):
    id = row['id']
    name = entity.value(NAME_FIELD)
    geocode = row['doc']['geometry'].get('coordinates')
    location = sequence_to_str(entity.location_path)
    mobile_number = entity.value(MOBILE_NUMBER_FIELD)
    description = entity.value(DESCRIPTION_FIELD)
    return dict(id=id, name=name, short_name=short_code, type=type, geocode=geocode, location=location,
                description=description, mobile_number=mobile_number)


def _get_entity_type_from_row(row):
    type = row['doc']['aggregation_paths']['_type']
    return type


def _get_entity_for_row(manager, row, type):
    short_code = row['doc']['short_code']
    entity = get_by_short_code(dbm=manager, short_code=short_code, entity_type=type)
    return entity, short_code


def load_all_subjects(request):
    manager = get_database_manager(request)
    rows = get_all_entities(dbm=manager, include_docs=True)
    data = []
    for row in rows:
        type = _get_entity_type_from_row(row)
        entity, short_code = _get_entity_for_row(manager, row, type)
        type = '.'.join(type)
        if type.lower() != 'reporter':
            data.append(_tabulate_data(entity, row, short_code, type))
    return data


def load_all_subjects_of_type(request, entity_type="reporter"):
    manager = get_database_manager(request)
    rows = get_all_entities(dbm=manager, include_docs=True)
    data = []
    for row in rows:
        type = _get_entity_type_from_row(row)
        entity, short_code = _get_entity_for_row(manager, row, type)
        type = '.'.join(type)
        if type.lower() == entity_type:
            data.append(_tabulate_data(entity, row, short_code, type))
    return data


def _handle_uploaded_file(file_name,file,manager):
    base_name, extension = os.path.splitext(file_name)
    if extension == '.csv':
        file = file.splitlines()
        csv_player = CsvPlayer(dbm=manager, submission_handler=SubmissionHandler(manager), parser=CsvParser())
        response = csv_player.accept(file)
    elif extension == '.xls':
        xls_player = XlsPlayer(dbm=manager, submission_handler=SubmissionHandler(manager), parser=XlsParser())
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