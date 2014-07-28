import itertools
import json
import os
import re
from xml.etree import ElementTree as ET

from django.http import HttpResponse
from lxml import etree
import xlrd
import xmldict
from pyxform import create_survey_element_from_dict
from pyxform.xls2json import parse_file_to_json

from datawinners.project.wizard_view import create_questionnaire

from mangrove.errors.MangroveException import QuestionAlreadyExistsException, QuestionCodeAlreadyExistsException, \
    EntityQuestionAlreadyExistsException
from datawinners.accountmanagement.models import NGOUserProfile
from datawinners.main.database import get_database_manager
from datawinners.project.helper import generate_questionnaire_code, associate_account_users_to_project
from mangrove.form_model.field import FieldSet, GeoCodeField, DateField

# used for edit questionnaire in xls questionnaire flow
# noinspection PyUnresolvedReferences
from datawinners.search import *
from mangrove.transport.player.parser import XlsParser
from django.utils.translation import ugettext as _


def get_generated_xform_id_name(xform):
    xform_cleaned = re.sub(r"\s+", " ", re.sub(r"\n", "", xform))
    match = re.search('<model>.* <instance> <(.+) id="', xform_cleaned)
    return match.group(1)


class XlsFormParser():
    type_dict = {'group': ['repeat', 'group'],
                 'field': ['text', 'integer', 'decimal', 'date', 'geopoint', 'calculate', 'cascading_select'],
                 'auto_filled': ['note', 'start', 'end', 'today', 'deviceid', 'subscriberid', 'imei', 'phonenumber'],
                 'select': ['select one', 'select all that apply']
    }
    recognised_types = list(itertools.chain(*type_dict.values()))
    supported_types = [type for type in recognised_types if type not in type_dict['auto_filled']]

    def __init__(self, path_or_file, questionnaire_name):
        self.questionnaire_name = questionnaire_name
        if isinstance(path_or_file, basestring):
            self._file_object = None
            path = path_or_file
        else:
            self._file_object = path_or_file
            path = path_or_file.name

        self.xform_dict = parse_file_to_json(path, file_object=path_or_file)

    def _validate_for_uppercase_names(self, field):
        if filter(lambda x: x.isupper(), field['name']):
            raise UppercaseNamesNotSupportedException()

    def _create_question(self, field):
        question = None
        if field['type'] in self.type_dict['group']:
            question = self._group(field)
        elif field['type'] in self.type_dict['field']:
            question = self._field(field)
        elif field['type'] in self.type_dict['select']:
            question = self._select(field)
        elif field['type'] in self.type_dict['media']:
            question = self._media(field)
        return question

    def _create_questions(self, fields):
        questions = []
        for field in fields:
            if field.get('control'):
                continue
            if field['type'] in self.supported_types:
                questions.append(self._create_question(field))
        return questions

    def _validate_fields_are_recognised(self, fields):
        for field in fields:
            self._validate_for_single_language(field)
            if field['type'] in self.recognised_types:
                if field['type'] in self.type_dict['group']:
                    if field['type'] == 'repeat' :
                        self._validate_for_nested_repeats(field)
                    self._validate_for_uppercase_names(field)
                    self._validate_fields_are_recognised(field['children'])
            else:
                raise TypeNotSupportedException("question type '" + field['type'] + "' is not supported")

    def _validate_for_nested_repeats(self, field):
        for f in field["children"]:
            if f["type"] == "repeat":
                raise NestedRepeatsNotSupportedException()
            if f["type"]=="group":
                self._validate_for_nested_repeats(f)

    def _validate_for_single_language(self, field):
        if 'label' in field and isinstance(field['label'], dict) and len(field['label']) > 1:
            raise MultipleLanguagesNotSupportedException()

    def parse(self):
        self._validate_fields_are_recognised(self.xform_dict['children'])
        questions = self._create_questions(self.xform_dict['children'])
        if not questions:
            raise Exception("Uploaded file is empty!")
        survey = create_survey_element_from_dict(self.xform_dict)
        xform = survey.to_xml()
        updated_xform = self.update_xform_with_questionnaire_name(xform)
        return updated_xform, questions

    def update_xform_with_questionnaire_name(self, xform):
        return re.sub(r"<h:title>\w+</h:", "<h:title>%s</h:" % self.questionnaire_name, xform)

    def _get_label(self, field):

        if 'label' not in field:
            return 'fixthis'

        if isinstance(field['label'], dict):
            return field['label'].values()[0]
        else:
            return field['label']

    def _group(self, field):
        group_label = self._get_label(field)

        fieldset_type = 'entity'

        if field['type'] == 'repeat':
            fieldset_type = 'repeat'
        elif field['type'] == 'group':
            fieldset_type = 'group'

        if not group_label:  # todo create appropriate error class
            raise QuestionAlreadyExistsException('Unique repeat label is required')
        name = field['name'].lower()
        questions = self._create_questions(field['children'])
        question = {
            'title': group_label,
            'type': 'field_set',
            "is_entity_question": False,
            "code": name, "name": group_label,
            "required": False,
            "instruction": "No answer required",
            "fieldset_type": fieldset_type,
            "fields": questions
        }
        return question

    def _field(self, field):
        xform_dw_type_dict = {'geopoint': 'geocode', 'decimal': 'integer', 'calculate': 'integer'}
        help_dict = {'text': 'word', 'integer': 'number', 'decimal': 'decimal or number', 'calculate': 'number'}
        name = self._get_label(field)
        code = field['name']
        type = field['type']

        question = {'title': name, 'type': xform_dw_type_dict.get(type, type), "is_entity_question": False,
                    "code": code, "name": name, 'required': self.is_required(field),
                    "instruction": "Answer must be a %s" % help_dict.get(type, type)}  # todo help text need improvement
        if type == 'date':
            question.update({'date_format': 'dd.mm.yyyy', 'event_time_field_flag': False,
                             "instruction": "Answer must be a date in the following format: day.month.year. Example: 25.12.2011"})
        return question

    def _select(self, field):
        name = self._get_label(field)
        code = field['name']
        if field.get('choices'):
            choices = [{'value': {'text': f.get('label') or f['name'], 'val': f['name']}} for f in field.get('choices')]
        else:
            choices = [{'value': {'text': f.get('label') or f['name'], 'val': f['name']}} for f in
                       self.xform_dict['choices'].get(field['itemset'])]
        question = {"title": name, "code": code, "type": "select", 'required': self.is_required(field),
                    "choices": choices, "is_entity_question": False}
        if field['type'] == 'select one':
            question.update({"type": "select1"})
        return question

    def is_required(self, field):
        if field.get('bind') and 'yes' == str(field['bind'].get('required')).lower():
            return True
        return False

    def _media(self, field):
        name = self._get_label(field)
        code = field['name']
        question = {"title": name, "code": code, "type": "image", 'required': self.is_required(field),
                    "is_entity_question": False}
        return question


class MangroveService():
    def __init__(self, user, xform_as_string, json_xform_data, questionnaire_code=None, project_name=None,
                 xls_form=None):
        self.user = user
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

        try:
            questionnaire = create_questionnaire(post=project_json, manager=self.manager, name=self.name,
                                                 language=self.language,
                                                 reporter_id=self.reporter_id, question_set_json=self.json_xform_data,
                                                 xform=self.xform_with_form_code)
            associate_account_users_to_project(self.manager, questionnaire)

        except (QuestionCodeAlreadyExistsException, QuestionAlreadyExistsException,
                EntityQuestionAlreadyExistsException) as ex:
            return HttpResponse(
                json.dumps({'success': False, 'error_message': _(ex.message), 'error_in_project_section': False}))

        code_has_errors, name_has_errors = False, False
        error_message = {}
        if not questionnaire.is_form_code_unique():
            code_has_errors = True
            error_message["code"] = _("Questionnaire with same code already exists.")
        if not questionnaire.is_project_name_unique():
            name_has_errors = True
            error_message["name"] = _("Questionnaire with same name already exists.")
        if not code_has_errors and not name_has_errors:
            questionnaire.update_doc_and_save()
            questionnaire.add_attachments(self.xls_form, 'questionnaire.xls')
            # UserActivityLog().log(request, action=CREATED_PROJECT, project=questionnaire.name,
            # detail=questionnaire.name)
            return questionnaire.id, self.name, error_message
        return None, None, error_message


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
            d.update(self.get_dict(f, submission_values.get(f.code, '')))
        s.update({project_name: d})
        return xmldict.dict_to_xml(s)


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
        self.message = _("multiple languages not supported")

    def __str__(self):
        return self.message


class UppercaseNamesNotSupportedException(Exception):
    def __init__(self):
        self.message = _("Uppercase in names not supported")

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
