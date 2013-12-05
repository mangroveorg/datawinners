from django.utils.translation import ugettext_lazy as _
import xlwt


def get_styles():
    bold = xlwt.easyfont('bold true, height 220, name Helvetica Neue')
    brown = xlwt.easyfont('color_index brown, name Helvetica Neue, height 220')
    italic = xlwt.easyfont('color_index gray50, italic true, name Helvetica Neue, height 220')
    gray = xlwt.easyfont('color_index gray50, name Helvetica Neue, height 220')
    return bold, brown, italic, gray


def get_subject_headers(fields):
    headers = []
    bold, brown, italic, gray = get_styles()
    for field in fields:
        context = InstructionContext(field=field, entity_type=None)
        instruction, example = SubjectInstructionBuilder.fetch_instruction(context)
        headers.append(((field["label"], bold), (u"\n%s" % instruction, brown), (u"\n\n%s" % example, italic)))
    return headers

def get_submission_headers(fields, form_model):
    headers = []
    bold, brown, italic, gray = get_styles()
    for field in fields:
        context = InstructionContext(field, form_model.entity_type[0])
        instruction, example = SubmissionInstructionBuilder.fetch_instruction(context)
        headers.append(((field["label"], bold), (u"\n\n%s" % instruction, gray), (u"\n\n%s" % example, italic)))
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
                return _("Answer must be a number between %s-%s.") % (min, max), ""
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
        return _("Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy."), _("Example: -18.1324,27.6547")


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
            "mm.yyyy": (_("Answer must be a date in the following format: month.year"), _("Example: 12.2011")),
            "dd.mm.yyyy": (_("Answer must be a date in the following format: day.month.year"), _("Example: 25.12.2011")),
            "mm.dd.yyyy": (_("Answer must be a date in the following format: month.day.year"), _("Example: 12.25.2011"))
        }
        return date_format_mapping.get(context.field["date_format"])


class EntityIdRegistrationInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field.get("entity_question_flag", False)

    @staticmethod
    def get_instruction(context):
        return _("Assign a unique ID for each Subject."), _(
            "Leave this column blank if you want DataWinners to assign an ID for you.")


class SummaryProjectSubmissionInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field.get("entity_question_flag", False) and context.entity_type == "reporter"

    @staticmethod
    def get_instruction(context):
        return _("If you are sending data on behalf of someone, you can enter their Data Sender ID."), \
               _("Example: rep42")

class EntityProjectSubmissionInstruction:
    @staticmethod
    def matches_criteria(context):
        return context.field.get("entity_question_flag", False) and context.entity_type != "reporter"

    @staticmethod
    def get_instruction(context):
        return _("Enter the unique ID for each %s.\nYou can find the %s List on the My Subjects page." % (context.entity_type, context.entity_type)), \
               _("Example: cli01")

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
    field_instructions = [SummaryProjectSubmissionInstruction, EntityProjectSubmissionInstruction, IntegerFieldInstruction, TextFieldInstruction,
                          GeoCodeFieldInstruction, DateFieldInstruction, MultiSelectFieldInstruction,
                          SingleSelectFieldInstruction]

    @classmethod
    def fetch_instruction(cls, context):
        for field_instruction in cls.field_instructions:

            if field_instruction.matches_criteria(context):
                return field_instruction.get_instruction(context)
        return None

class InstructionContext():

    def __init__(self, field, entity_type):
        self.field = field
        self.entity_type = entity_type