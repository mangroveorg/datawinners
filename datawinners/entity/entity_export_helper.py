from django.utils.translation import ugettext_lazy as _
import xlwt


def get_styles():
    bold = xlwt.easyfont('bold true, height 220, name Helvetica Neue')
    brown = xlwt.easyfont('color_index brown, name Helvetica Neue, height 220')
    italic = xlwt.easyfont('italic true, name Helvetica Neue, height 220')
    return bold, brown, italic


def get_subject_headers(fields):
    headers = []
    bold, brown, italic = get_styles()
    for field in fields:
        instruction, example = SubjectInstructionBuilder.fetch_instruction(field)
        headers.append(((field["label"], bold), (u"\n %s" % instruction, brown), (u"\n\n %s" % example, italic)))
    return headers


def get_submission_headers(fields):
    headers = []
    bold, brown, italic = get_styles()
    for field in fields:
        instruction, example = SubmissionInstructionBuilder.fetch_instruction(field)
        headers.append(((field["label"], bold), (u"\n %s" % instruction, brown), (u"\n\n %s" % example, italic)))
    return headers


class TextFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "text"

    @staticmethod
    def get_instruction(field):
        if "constraints" in field and field["constraints"][0][0] == "length" and "max" in field["constraints"][0][1]:
            return _("Enter a Word with a maximum %s of characters.") % field["constraints"][0][1].get("max"), ""
        return _("Enter a word"), ""


class IntegerFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "integer"

    @staticmethod
    def get_instruction(field):
        if "constraints" in field and field["constraints"][0][0] == "range":
            max = field["constraints"][0][1].get("max")
            min = field["constraints"][0][1].get("min")
            if max and min:
                return _("Enter a number between %s-%s.") % (min, max), ""
            if max and not min:
                return _("Enter a number. The maximum is %s") % max, ""
            if not max and min:
                return _("Enter a number. The minimum is %s") % min, ""
            return _("Enter a number"), ""


class GeoCodeFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "geocode"

    @staticmethod
    def get_instruction(field):
        return _("Enter GPS co-ordinates in the following format: xx.xxxx,yy.yyyy."), _("Example: -18.1324,27.6547")


class ListFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "list"

    @staticmethod
    def get_instruction(field):
        return _("Enter name of the location."), _("Example: Nairobi")


class SingleSelectFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "select1"

    @staticmethod
    def get_instruction(field):
        return _("Enter 1 answer from the list."), _("Example: a")


class MultiSelectFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "select"

    @staticmethod
    def get_instruction(field):
        return _("Choose 1 or more answers from the list."), _("Example: a or ab")


class TelephoneNumberFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "telephone_number"

    @staticmethod
    def get_instruction(field):
        return _("Enter a telephone number along with the country code."), _("Example: 261333745269")


class DateFieldInstruction:
    @staticmethod
    def matches_criteria(field):
        return field["type"] == "date"

    @staticmethod
    def get_instruction(field):
        date_format_mapping = {
            "mm.yyyy": (_("Enter the date in the following format: month.year"), _("Example: 12.2011")),
            "dd.mm.yyyy": (_("Enter the date in the following format: day.month.year"), _("Example: 25.12.2011")),
            "mm.dd.yyyy": (_("Enter the date in the following format: month.day.year"), _("Example: 12.25.2011"))
        }
        return date_format_mapping.get(field["date_format"])


class EntityIdRegistrationInstruction:
    @staticmethod
    def matches_criteria(field):
        return field.get("entity_question_flag", False)

    @staticmethod
    def get_instruction(field):
        return _("Assign a unique ID for each Subject."), _(
            "Leave this column blank if you want DataWinners to assign an ID for you.")


class EntityIdSubmissionInstruction:
    @staticmethod
    def matches_criteria(field):
        return field.get("entity_question_flag", False)

    @staticmethod
    def get_instruction(field):
        return _("Enter unique ID"), ""


class SubjectInstructionBuilder:
    field_instructions = [EntityIdRegistrationInstruction, IntegerFieldInstruction, TextFieldInstruction,
                          GeoCodeFieldInstruction, DateFieldInstruction, MultiSelectFieldInstruction,
                          SingleSelectFieldInstruction, TelephoneNumberFieldInstruction, ListFieldInstruction]

    @classmethod
    def fetch_instruction(cls, field):
        for field_instruction in cls.field_instructions:
            if field_instruction.matches_criteria(field):
                return field_instruction.get_instruction(field)
        return None


class SubmissionInstructionBuilder:
    field_instructions = [EntityIdSubmissionInstruction, IntegerFieldInstruction, TextFieldInstruction,
                          GeoCodeFieldInstruction, DateFieldInstruction, MultiSelectFieldInstruction,
                          SingleSelectFieldInstruction]

    @classmethod
    def fetch_instruction(cls, field):
        for field_instruction in cls.field_instructions:
            if field_instruction.matches_criteria(field):
                return field_instruction.get_instruction(field)
        return None
