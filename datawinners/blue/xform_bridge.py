import itertools
import os
import re
from xml.etree import ElementTree as ET

from lxml import etree
from mangrove.datastore.entity_type import entity_type_already_defined
from pyxform.xls2json import parse_file_to_json
import xlrd
import xmldict
from pyxform import create_survey_element_from_dict
from datawinners.activitylog.models import UserActivityLog
from datawinners.common.constant import CREATED_QUESTIONNAIRE

from datawinners.project.wizard_view import create_questionnaire
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.main.database import get_database_manager
from datawinners.project.helper import generate_questionnaire_code, associate_account_users_to_project
from mangrove.form_model.field import FieldSet, GeoCodeField, DateField, PhotoField, VideoField, AudioField, MediaField, \
    SelectField


# used for edit questionnaire in xls questionnaire flow
# noinspection PyUnresolvedReferences
from datawinners.search import *
from mangrove.transport.player.parser import XlsParser
from django.utils.translation import ugettext as _
from xml.sax.saxutils import escape


def get_generated_xform_id_name(xform):
    xform_cleaned = re.sub(r"\s+", " ", re.sub(r"\n", "", xform))
    match = re.search('<model>.* <instance> <(.+?) id="', xform_cleaned)
    return match.group(1)


CALCULATE = 'calculate'
BARCODE = 'barcode'


class XlsFormParser():
    type_dict = {'group': ['repeat', 'group'],
                 'field': ['text', 'integer', 'decimal', 'date', 'geopoint', 'calculate', 'cascading_select', BARCODE,
                           'time', 'datetime', 'unique_id'],
                 'auto_filled': ['note', 'today'],
                 'media': ['photo', 'audio', 'video'],
                 'select': ['select one', 'select all that apply', 'select one or specify other',
                            'select all that apply or specify other']
    }
    meta_data_types = ["start", "end", "today", "imei", "deviceid", "subscriberid", "phonenumber", "simserial"]
    recognised_types = list(itertools.chain(*type_dict.values()))
    supported_types = [type for type in recognised_types if type not in type_dict['auto_filled']]
    or_other_data_types = ['select all that apply or specify other', 'select one or specify other']
    select_without_list_name = ['select_one', 'select_multiple']

    def __init__(self, path_or_file, questionnaire_name, dbm=None):
        self.questionnaire_name = questionnaire_name
        self.dbm = dbm
        if isinstance(path_or_file, basestring):
            self._file_object = None
            path = path_or_file
        else:
            self._file_object = path_or_file
            path = path_or_file.name

        self.xform_dict = parse_file_to_json(path, file_object=path_or_file)

    def _validate_for_uppercase_names(self, field):
        if filter(lambda x: x.isupper(), field['name']):
            return _("Uppercase in names not supported")
        return None

    def _create_question(self, field, parent_field_code=None):
        question = None
        errors = []
        field_type = field['type'].lower()
        if field_type in self.type_dict['group']:
            question, errors = self._group(field, parent_field_code)
        elif field_type in self.type_dict['field']:
            question = self._field(field, parent_field_code)
        elif field_type in self.type_dict['select']:
            question = self._select(field, parent_field_code)
        elif field_type in self.type_dict['media']:
            question = self._media(field, parent_field_code)
        return question, errors

    def _create_questions(self, fields, parent_field_code=None):
        questions = []
        errors = []
        for field in fields:
            if field.get('control', None) and field['control'].get('bodyless', False):  # ignore calculate type
                continue
            if field['type'].lower() in self.supported_types:
                try:
                    question, field_errors = self._create_question(field, parent_field_code)

                    if not field_errors and question:
                        questions.append(question)

                        if question['type'] in ['select', 'select1'] and question['has_other']:
                            other_field = {u'type': u'text', u'name': question['code'] + "_other",
                                           u'label': question['title'] + "_other"}
                            other_question, other_field_errors = self._create_question(other_field, parent_field_code)
                            questions.append(other_question)

                    else:
                        errors.extend(field_errors)
                except LabelForChoiceNotPresentException as e:
                    errors.append(e.message)
                except UniqueIdNotFoundException as e:
                    errors.append(e.message)
                except LabelForFieldNotPresentException as e:
                    errors.append(e.message)
        return questions, set(errors)

    def _validate_group(self, errors, field):
        if field['type'] == 'repeat':
            try:
                self._validate_for_nested_repeats(field)
            except NestedRepeatsNotSupportedException as e:
                errors.append(e.message)
        child_errors = self._validate_fields_are_recognised(field['children'])
        errors.extend(child_errors)

    def _validate_fields_are_recognised(self, fields):
        errors = []
        for field in fields:
            try:
                self._validate_for_no_language(field)
            except MultipleLanguagesNotSupportedException as e:
                errors.append(e.message)
            field_type = field['type'].lower()
            if field_type in self.recognised_types:
                if field_type in self.type_dict['group']:
                    self._validate_group(errors, field)
                # errors.append(self._validate_for_uppercase_names(field))
                errors.append(self._validate_for_prefetch_csv(field))
            else:
                if (field["type"] in self.meta_data_types):
                    errors.append(_("%s as a datatype (metadata)") % _(field_type))
                # elif(field["type"]) in self.or_other_data_types:
                # errors.append(_("XLSForm \"or_other\" function for multiple choice or single choice questions"))
                elif (field["type"]) in self.select_without_list_name:
                    errors.append(_("missing list reference, check your select_one or select multiple question types"))
                else:
                    errors.append(_("%s as a datatype") % _(field_type))
            if field.get('media'):
                for media_type in field['media'].keys():
                    errors.append(_("attaching media to fields is not supported %s") % media_type)
        return set(errors) - set([None])

    def _validate_for_nested_repeats(self, field):
        for f in field["children"]:
            if f["type"] == "repeat":
                raise NestedRepeatsNotSupportedException()
            if f["type"] == "group":
                self._validate_for_nested_repeats(f)

    def _validate_for_no_language(self, field):
        for header in ['label', 'hint']:
            if self._has_languages(field.get(header)):
                raise MultipleLanguagesNotSupportedException()
        field.get("choices") and self._validate_for_no_language(field.get("choices")[0])
        if field.get('bind') and self._has_languages(field.get('bind').get('jr:constraintMsg')):
            raise MultipleLanguagesNotSupportedException()

    def _has_languages(self, header):
        return header and isinstance(header, dict) and len(header) >= 1

    @staticmethod
    def _get_media_in_choices(choices):
        for choice in choices:
            if choice.get('media'):
                return choice['media'].keys()
        return []

    def _validate_media_in_choices(self, fields):
        errors = []
        for field in fields:
            if field['type'] in self.type_dict['group']:
                choice_errors = self._validate_media_in_choices(field['children'])
                [errors.append(choice_error) for choice_error in choice_errors if choice_error]
            choices = field.get('choices')
            if choices:
                media_type_in_choices = self._get_media_in_choices(choices)
                for media_type in media_type_in_choices:
                    errors.append(_("attaching media to choice fields not supported %s") % _(media_type))
        return errors

    def _validate_choice_names(self, fields):
        errors = []
        for field in fields:
            if field['type'] in self.type_dict['group']:
                errors.extend(self._validate_choice_names(field['children']))
            choices = field.get('choices')
            if choices:
                name_list = [choice['name'].lower() for choice in choices]
                name_list_without_duplicates = list(set(name_list))
                if len(name_list) != len(name_list_without_duplicates):
                    errors.append(_("duplicate names within one list (choices sheet)"))
                if filter(lambda name: " " in unicode(name), name_list):
                    errors.append(_("spaces in name column (choice sheet)"))
        return errors

    def parse(self):
        fields = self.xform_dict['children']
        errors = self._validate_fields_are_recognised(fields)
        settings_page_errors = self._validate_settings_page_is_not_present(self.xform_dict)
        errors = errors.union(settings_page_errors)
        choice_errors = self._validate_media_in_choices(fields)
        [errors.add(choice_error) for choice_error in choice_errors if choice_error]
        choice_name_errors = self._validate_choice_names(fields)
        errors = errors.union(set(choice_name_errors))
        questions, question_errors = self._create_questions(fields)
        if question_errors:
            errors = errors.union(question_errors)
        if not errors and not questions:
            errors.add("Uploaded file is empty!")
        if errors:
            return errors, None, None
        _map_unique_id_question_to_select_one(self.xform_dict)
        survey = create_survey_element_from_dict(self.xform_dict)
        xform = survey.to_xml()
        # encoding is added to support ie8
        xform = re.sub(r'<\?xml version="1.0"\?>', '<?xml version="1.0" encoding="utf-8"?>', xform)
        updated_xform = self.update_xform_with_questionnaire_name(xform)
        return [], updated_xform, questions


    def update_xform_with_questionnaire_name(self, xform):
        return re.sub(r"<h:title>\w+</h:", "<h:title>%s</h:" % escape(self.questionnaire_name), xform)

    def _get_label(self, field):

        if 'label' not in field:
            if field['type'] == 'group' and 'control' in field:
                if field['control']['appearance'] == 'field-list':
                    return field['name']
            elif field['type'] == 'calculate':
                return field['name']
            else:
                raise LabelForFieldNotPresentException(field_name=field['name'])

        if isinstance(field['label'], dict):
            return field['label'].values()[0]
        else:
            return field['label']

    def _group(self, field, parent_field_code=None):
        group_label = self._get_label(field)

        fieldset_type = 'entity'

        if field['type'] == 'repeat':
            fieldset_type = 'repeat'
        elif field['type'] == 'group':
            fieldset_type = 'group'

        name = field['name']
        questions, errors = self._create_questions(field['children'], field['name'])
        question = {
            'title': group_label,
            'type': 'field_set',
            "is_entity_question": False,
            "code": name, "name": group_label,
            "required": False,
            "parent_field_code": parent_field_code,
            "instruction": "No answer required",
            "fieldset_type": fieldset_type,
            "fields": questions
        }
        return question, errors

    def _get_date_format(self, field):

        if field['type'] == 'time':
            return "HH:mm"

        appearance = self._get_appearance(field)
        if appearance:
            if 'month-year' in appearance:
                return 'mm.yyyy'
            if 'year' in appearance:
                return 'yyyy'
        return 'dd.mm.yyyy'

    def _field(self, field, parent_field_code=None):
        xform_dw_type_dict = {'geopoint': 'geocode', 'decimal': 'integer', CALCULATE: 'text', BARCODE: 'text'}
        help_dict = {'text': 'word', 'integer': 'number', 'decimal': 'decimal or number', CALCULATE: 'calculated field'}
        name = self._get_label(field)
        code = field['name']
        type = field['type'].lower()

        question = {'title': name, 'type': xform_dw_type_dict.get(type, type), "is_entity_question": False,
                    "code": code, "name": name, 'required': self.is_required(field),
                    "parent_field_code": parent_field_code,
                    "instruction": "Answer must be a %s" % help_dict.get(type, type)}  # todo help text need improvement
        if type in ['date']:
            format = self._get_date_format(field)
            question.update({'date_format': format, 'event_time_field_flag': False,
                             "instruction": "Answer must be a date in the following format: day.month.year. Example: 25.12.2011"})

        if type == 'unique_id':
            try:
                unique_id_type = field['bind']['constraint']
                if not entity_type_already_defined(self.dbm, [unique_id_type]):
                    raise UniqueIdNotFoundException(field['name'])
                question.update({'uniqueIdType': unique_id_type})
            except KeyError:
                raise UniqueIdNotFoundException(field['name'])

        if type == CALCULATE:
            question.update({"is_calculated": True})

        return question

    def _get_appearance(self, field):
        if field.get('control') and field['control'].get('appearance'):
            return field['control']['appearance']

    def _select(self, field, parent_field_code=None):
        if self._get_appearance(field) == 'label':
            return
        name = self._get_label(field)
        code = field['name']
        if field.get('choices'):
            choices = [{'value': {'text': self._get_choice_label(f), 'val': f['name']}} for f in field.get('choices')]
        else:
            # cascade select
            choices = [{'value': {'text': self._get_choice_label(f), 'val': f['name']}} for f in
                       self.xform_dict['choices'].get(field['itemset'])]
        question = {"title": name, "code": code, "type": "select", 'required': self.is_required(field),
                    "parent_field_code": parent_field_code,
                    "choices": choices, "is_entity_question": False}

        question.update({"has_other": field['type'] in self.or_other_data_types})

        if field['type'] in ['select one', 'select one or specify other']:
            question.update({"type": "select1"})

        return question

    def _get_choice_label(self, choice_field):
        if not choice_field.get('label', None):
            raise LabelForChoiceNotPresentException(choice_field.get('name', ''))

        return choice_field.get('label')

    def is_required(self, field):
        if field.get('bind') and 'yes' == str(field['bind'].get('required')).lower():
            return True
        return False

    def _media(self, field, parent_field_code=None):
        name = self._get_label(field)
        code = field['name']
        question = {"title": name, "code": code, "type": field['type'], 'required': self.is_required(field),
                    "parent_field_code": parent_field_code,
                    "is_entity_question": False}
        return question

    def _validate_for_prefetch_csv(self, field):
        if 'bind' in field and 'calculate' in field['bind'] and 'pulldata(' in field['bind']['calculate']:
            return _("Prefetch of csv not supported")
        return None

    def _validate_settings_page_is_not_present(self, xform_dict):
        errors = []
        setting_page_error = _("XLSForm settings worksheet and the related values in survey sheet.")
        if xform_dict['title'] != xform_dict['name']:
            errors.append(setting_page_error)

        if xform_dict['id_string'] != xform_dict['name']:
            errors.append(setting_page_error)

        if xform_dict['default_language'] != 'default':
            errors.append(setting_page_error)

        if 'public_key' in xform_dict:
            errors.append(setting_page_error)

        if 'submission_url' in xform_dict:
            errors.append(setting_page_error)

        return set(errors)


def _map_unique_id_question_to_select_one(xform_dict):
    for field in xform_dict['children']:
        if field['type'] == "unique_id":
            field['type'] = 'select one'
            field[u'choices'] = [{u'name': field['name'], u'label':u'placeholder'}]
            del field['bind']['constraint']
        elif field['type'] in ['group', 'repeat']:
            _map_unique_id_question_to_select_one(field)

class MangroveService():
    def __init__(self, request, xform_as_string, json_xform_data, questionnaire_code=None, project_name=None,
                 xls_form=None):
        self.request = request
        self.user = request.user
        user_profile = NGOUserProfile.objects.get(user=self.user)
        self.reporter_id = user_profile.reporter_id
        self.manager = get_database_manager(self.user)
        self.entity_type = ['reporter']
        self.questionnaire_code = questionnaire_code if questionnaire_code else generate_questionnaire_code(
            self.manager)
        self.name = 'Xlsform-Project-' + self.questionnaire_code if not project_name else project_name
        self.language = 'en'
        self.xform = xform_as_string
        self.xform_with_form_code = self.add_form_code(xform_as_string, self.questionnaire_code)
        self.json_xform_data = json_xform_data
        self.xls_form = xls_form

    def _add_model_sub_element(self, root, name, value):
        generated_id = get_generated_xform_id_name(self.xform)
        model = '{http://www.w3.org/2002/xforms}%s' % generated_id
        [self._add(r, name, value) for r in root.iter(model)]

        node_set = '/%s/%s' % (generated_id, name)
        [ET.SubElement(r, '{http://www.w3.org/2002/xforms}bind', {'nodeset': node_set, 'type': "string"}) for r in
         root.getiterator() if
         r.tag == '{http://www.w3.org/2002/xforms}model']

    def _add(self, instance, name, value):
        e = ET.SubElement(instance, '{http://www.w3.org/2002/xforms}%s' % name)
        e.text = value
        return e

    def add_form_code(self, xform, form_code):
        ET.register_namespace('', 'http://www.w3.org/2002/xforms')
        root = ET.fromstring(xform.encode('utf-8'))
        self._add_model_sub_element(root, 'form_code', form_code)
        return '<?xml version="1.0"?>%s' % ET.tostring(root)

    def create_project(self):
        project_json = {'questionnaire-code': self.questionnaire_code}

        questionnaire = create_questionnaire(post=project_json, manager=self.manager, name=self.name,
                                             language=self.language,
                                             reporter_id=self.reporter_id, question_set_json=self.json_xform_data,
                                             xform=self.xform_with_form_code)

        if not questionnaire.is_project_name_unique():
            return None, None

        associate_account_users_to_project(self.manager, questionnaire)
        questionnaire.update_media_field_flag()
        questionnaire.update_doc_and_save()
        questionnaire.add_attachments(self.xls_form, 'questionnaire.xls')
        UserActivityLog().log(self.request, action=CREATED_QUESTIONNAIRE, project=questionnaire.name,
                              detail=questionnaire.name)
        return questionnaire.id, questionnaire.form_code


def _is_choice_item_in_choice_list(item, options):
    for choice_item in options:
        if choice_item['val'] == item:
            return True
    return False


class XFormSubmissionProcessor():
    def get_dict(self, field, value):
        if not value:
            return {field.code: ''}
        if type(field) is FieldSet:
            dicts = []
            for v in value:
                dict = {}
                for f in field.fields:
                    dict.update(self.get_dict(f, v.get(f.code, '')))
                dicts.append(dict)
            return {field.code: dicts}
        elif type(field) is DateField:
            return {field.code: '-'.join(value.split('.')[::-1])}
        elif type(field) is GeoCodeField:
            return {field.code: value.replace(',', ' ')}
        else:
            return {field.code: value}

    def get_model_edit_str(self, form_model_fields, submission_values, project_name, form_code):
        # todo instead of using form_model fields, use xform to find the fields
        d, s = {'form_code': form_code}, {}
        for f in form_model_fields:
            answer = submission_values.get(f.code, '')
            if isinstance(f, SelectField) and f.has_other and isinstance(answer, list) and answer[0] == 'other':
                if f.is_single_select:
                    d.update({f.code + "_other": answer[1]})
                    d.update({f.code: answer[0]})
                else:
                    other_selection = []
                    choice_selections = ['other']
                    for item in answer[1].split(' '):
                        if _is_choice_item_in_choice_list(item, f.options):
                            choice_selections.append(item)
                        else:
                            other_selection.append(item)
                    d.update({f.code + "_other": ' '.join(other_selection)})
                    d.update({f.code: ' '.join(choice_selections)})
            else:
                d.update(self.get_dict(f, answer))
        s.update({project_name: d})
        return xmldict.dict_to_xml(s)


class XFormImageProcessor():
    media_fields = [PhotoField, VideoField, AudioField]

    def get_media(self, field, value):
        if type(field) is FieldSet:
            file_names = []
            for v in value:
                for f in field.fields:
                    if isinstance(f, MediaField) and v.get(f.code, ''):
                        file_names.append(v.get(f.code, ''))
            return file_names
        if isinstance(field, MediaField):
            return [value]

    def get_media_files_str(self, form_model_fields, submission_values):
        media_files = []
        for f in form_model_fields:
            values = submission_values.get(f.code, '')
            if values and (isinstance(f, MediaField) or type(f) is FieldSet):
                media_files.extend(self.get_media(f, values))
        return ','.join(media_files)


DIR = os.path.dirname(__file__)


class XFormTransformer():
    def __init__(self, xform_as_string):
        self.xform = xform_as_string
        self.xls_folder = os.path.join(DIR, 'xsl')
        self.HTML_FORM = os.path.join(self.xls_folder, 'openrosa2html5form_php5.xsl')
        self.XML_MODEL = os.path.join(self.xls_folder, 'openrosa2xmlmodel.xsl')

    def transform(self):
        model_xslt = etree.XML(open(self.XML_MODEL, 'r').read())
        transform_model = etree.XSLT(model_xslt)
        model_doc = etree.fromstring(self.xform)
        model_tree = transform_model(model_doc)

        form_xslt = etree.XML(open(self.HTML_FORM, 'r').read())
        transform_form = etree.XSLT(form_xslt)
        form_doc = etree.fromstring(self.xform)
        form_tree = transform_form(form_doc)

        r = model_tree.getroot()
        r.extend(form_tree.getroot())
        return etree.tostring(r)


class TypeNotSupportedException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NestedRepeatsNotSupportedException(Exception):
    def __init__(self):
        self.message = _("nested repeats not supported")

    def __str__(self):
        return self.message


class MultipleLanguagesNotSupportedException(Exception):
    def __init__(self):
        self.message = _("Language specification is not supported")

    def __str__(self):
        return self.message


class LabelForChoiceNotPresentException(Exception):
    def __init__(self, choice_name):
        self.message = _("Label mandatory for choice option with name %s") % choice_name

    def __str__(self):
        return self.message


class PrefetchCSVNotSupportedException(Exception):
    def __init__(self):
        self.message = _("Prefetch of csv not supported")

    def __str__(self):
        return self.message


class LabelForFieldNotPresentException(Exception):
    def __init__(self, field_name):
        self.message = _("Label mandatory for question with name [%s]") % field_name

    def __str__(self):
        return self.message

class UniqueIdNotFoundException(Exception):
    def __init__(self, field_name):
        self.message = _("Valid UniqueId type not found in constraint column for field with name [%s]") % field_name

    def __str__(self):
        return self.message


class XlsProjectParser(XlsParser):
    def parse(self, xls_contents):
        assert xls_contents is not None
        workbook = xlrd.open_workbook(file_contents=xls_contents)
        xls_dict = {}
        for worksheet in workbook.sheets():
            parsedData = []
            for row_num in range(0, worksheet.nrows):
                row = worksheet.row_values(row_num)
                row = self._clean(row)
                parsedData.append(row)
            xls_dict[worksheet.name] = parsedData
        return xls_dict
