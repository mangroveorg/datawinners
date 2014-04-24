from django.utils.translation import ugettext_lazy as _, ugettext
import xlwt
from mangrove.form_model.field import UniqueIdField,ShortCodeField,field_attributes

BEHALF_OF = "I am submitting this data on behalf of"


def get_styles():
    bold = xlwt.easyfont('bold true, height 220, name Helvetica Neue')
    brown = xlwt.easyfont('color_index brown, name Helvetica Neue, height 220')
    italic = xlwt.easyfont('color_index gray50, italic true, name Helvetica Neue, height 220')
    gray = xlwt.easyfont('color_index gray50, name Helvetica Neue, height 220')
    return bold, brown, italic, gray


def add_to_header(headers, label, instruction, example):
    bold, brown, italic, gray = get_styles()
    headers.append(((label, bold), (u"\n\n%s" % instruction, brown), (u"\n\n%s" % example, italic)))


def get_subject_headers(fields):
    headers = []
    for field in fields:
        context = InstructionContext(field=field, unique_id_types=None)
        instruction, example = SubjectInstructionBuilder.fetch_instruction(context)
        add_to_header(headers, field["label"], instruction, example)
    return headers


def get_submission_headers(fields, form_model, is_org_user=False):
    headers = []

    if is_org_user:
        add_to_header(headers, BEHALF_OF,
                      _("If you are sending data on behalf of someone, you can enter their Data Sender ID. Otherwise you can leave it blank."), \
                  _("Example: rep42"))

    for field in fields:
        context = InstructionContext(field, form_model.entity_type)
        instruction, example = SubmissionInstructionBuilder.fetch_instruction(context)
        add_to_header(headers, field["label"], instruction, example)
    return headers


class TextFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "text"

    @staticmethod
    def get_instruction(context):
        field = context.field
        if "constraints" in field and field["constraints"][0][0] == "length" and "max" in field["constraints"][0][1]:
            return _("Answer must be a word %s characters maximum") % field["constraints"][0][1].get("max"), ""
        return _("Answer must be a word"), ""


class IntegerFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "integer"

    @staticmethod
    def get_instruction(context):
        field = context.field
        if "constraints" in field and field["constraints"][0][0] == "range":
            max = field["constraints"][0][1].get("max")
            min = field["constraints"][0][1].get("min")
            if max and min:
                return _("Enter a number between %s-%s.") % (min, max), ""
            if max and not min:
                return _("Answer must be a number. The maximum is %s") % max, ""
            if not max and min:
                return _("Answer must be a number. The minimum is %s") % min, ""
            return _("Enter a number"), ""


class GeoCodeFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "geocode"

    @staticmethod
    def get_instruction(context):
        return _("Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy."), _(
            "Example: -18.1324,27.6547")


class ListFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "list"

    @staticmethod
    def get_instruction(context):
        return _("Enter name of the location."), _("Example: Nairobi")


class SingleSelectFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "select1"

    @staticmethod
    def get_instruction(context):
        return _("Enter 1 answer from the list."), _("Example: a")


class MultiSelectFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "select"

    @staticmethod
    def get_instruction(context):
        return _("Enter 1 or more answers from the list."), _("Example: a or ab")


class TelephoneNumberFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "telephone_number"

    @staticmethod
    def get_instruction(context):
        return _("Answer must be country code plus telephone number"), _("Example: 261333745269")


class DateFieldInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field["type"] == "date"

    @staticmethod
    def get_instruction(context):
        date_format_mapping = {
            "mm.yyyy": (
                ugettext("Answer must be a date in the following format:") + " " + ugettext("month.year"),
                ugettext("Example: %s") % '12.2011'),
            "dd.mm.yyyy": (
                ugettext("Answer must be a date in the following format:") + " " + ugettext("day.month.year"),
                ugettext("Example: %s") % '25.12.2011'),
            "mm.dd.yyyy": ((ugettext("Answer must be a date in the following format:") + " " + ugettext("month.day.year")),
                           ugettext("Example: %s" % '12.25.2011'))
        }
        return date_format_mapping.get(context.field["date_format"])


class EntityIdRegistrationInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field.get("type") == field_attributes.SHORT_CODE_FIELD

    @staticmethod
    def get_instruction(context):
        return _("Assign a unique ID for each Subject."), _(
            "Leave this column blank if you want DataWinners to assign an ID for you.")


class EntityProjectSubmissionInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field.get("type") == field_attributes.UNIQUE_ID_FIELD

    @staticmethod
    def get_instruction(context):
        unique_id_type = context.field['unique_id_type']
        page_name = _("Identification Numbers") if context.has_multiple_unique_ids else "%s" % unique_id_type

        return _("Enter the unique ID for each %s.\nYou can find the %s List on the My %s page.") % (
            unique_id_type, unique_id_type, page_name), (_("Example: %s")) % 'cli01'


class SubjectInstructionBuilder:
    field_instructions = [EntityIdRegistrationInstruction, IntegerFieldInstruction, TextFieldInstruction,
                          GeoCodeFieldInstruction, DateFieldInstruction, MultiSelectFieldInstruction,
                          SingleSelectFieldInstruction, TelephoneNumberFieldInstruction, ListFieldInstruction]

    @classmethod
    def fetch_instruction(cls, context):
        for field_instruction in cls.field_instructions:
            if field_instruction.matches_criteria(context):
                return field_instruction.get_instruction(context)
        return None


class SubmissionInstructionBuilder:
    field_instructions = [
                          EntityProjectSubmissionInstruction,
                          IntegerFieldInstruction, TextFieldInstruction,
                          GeoCodeFieldInstruction, DateFieldInstruction, MultiSelectFieldInstruction,
                          SingleSelectFieldInstruction
                        ]

    @classmethod
    def fetch_instruction(cls, context):
        for field_instruction in cls.field_instructions:

            if field_instruction.matches_criteria(context):
                return field_instruction.get_instruction(context)
        return None


class InstructionContext():
    def __init__(self, field, unique_id_types):
        self.field = field
        self.has_multiple_unique_ids = unique_id_types is not None and len(unique_id_types) > 1