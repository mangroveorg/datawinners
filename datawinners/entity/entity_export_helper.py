from django.utils.translation import ugettext_lazy as _
import xlwt


def get_json_field_infos(fields):
    fields_names, labels, codes = [], [], []
    bold = xlwt.easyfont('bold true, height 220, name Helvetica Neue')
    brown = xlwt.easyfont('color_index brown, name Helvetica Neue, height 220')
    italic = xlwt.easyfont('italic true, name Helvetica Neue, height 220')
    for field in fields:
        if field['name'] != 'entity_type':
            fields_names.append(field['name'])
            instruction, example = _get_json_field_instruction_example(field)
            labels.append(((field["label"], bold), (u"\n %s" % instruction, brown), (u"\n\n %s" % example, italic)))
            codes.append(field['code'])
    return fields_names, labels, codes


def _get_json_field_instruction_example(field):
    if field.get("entity_question_flag", False):
        return _("Assign a unique ID for each Subject."), _(
            "Leave this column blank if you want DataWinners to assign an ID for you.")

    if field["type"] == "text":
        if "constraints" in field and field["constraints"][0][0] == "length" and "max" in field["constraints"][0][1]:
            return _("Enter a Word with a maximum %s of characters.") % field["constraints"][0][1].get("max"), ""
        return _("Enter a word"), ""

    if field["type"] == "integer":
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

    if field["type"] == "geocode":
        return _("Enter GPS co-ordinates in the following format: xx.xxxx,yy.yyyy."), _("Example: -18.1324,27.6547")

    if field["type"] == "list":
        return _("Enter name of the location."), _("Example: Nairobi")

    if field["type"] == "select1":
        return _("Enter 1 answer from the list."), _("Example: a")

    if field["type"] == "select":
        return _("Choose 1 or more answers from the list."), _("Example: a or ab")

    if field["type"] == "telephone_number":
        return _("Enter a telephone number along with the country code."), _("Example: 261333745269")

    date_format_mapping = {
        "mm.yyyy": (_("Enter the date in the following format: month.year"), _("Example: 12.2011")),
        "dd.mm.yyyy": (_("Enter the date in the following format: day.month.year"), _("Example: 25.12.2011")),
        "mm.dd.yyyy": (_("Enter the date in the following format: month.day.year"), _("Example: 12.25.2011"))
    }

    if field["type"] == "date":
        return date_format_mapping.get(field["date_format"])
    return field["instruction"], ""