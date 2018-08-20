import re

from django.utils.translation import ugettext

RECEIVED_ON = 'received_on'
STATUS_CHANGED = 'status_changed'
CHANGED_ANSWERS = 'changed_answers'
OLD = 'old'
NEW = 'new'


def get_questionnaire_detail(detail_dict):
    detail_list = []
    for edit_type in ["added", "deleted"]:
        if edit_type in detail_dict:
            detail_list.append("%s: %s" % (ugettext("%s Questions" % edit_type.capitalize()),
                                           _html(detail_dict, edit_type)))

    for attr in ["", "hint", "constraint_message", "constraint", "relevant", "required", "default", "appearance", "choice"]:
        edit_type = attr + "_changed" if attr else "changed"
        if edit_type in detail_dict:
            detail_list.append("%s: %s" % (ugettext("Question %s Changed" % (re.sub("_", " ", attr).capitalize() if attr else "Label")),
                                           _html(detail_dict, edit_type)))

    if "changed_type" in detail_dict:
        response_type = {"select1": "List of Choices", "select": "List of Choices", "text": "Word or Phrase",
                         "integer": "Number", "unique_id": "Identification Number",
                         "geocode": "GPS Coordinates", "date": "date", "telephone_number": "Telephone Number"}
        for type_changed in detail_dict["changed_type"]:
            detail_list.append(ugettext('Answer type changed to %(answer_type)s for \"%(question_label)s\"') %
                               {"answer_type": ugettext(response_type.get(type_changed["type"], "")),
                                "question_label": type_changed["label"]})

    return "<br/>".join(detail_list)


def _html(detail_dict, edit_type):
    html = '<ul class="bulleted">'
    for item in detail_dict[edit_type]:
        html += "<li>%s</li>" % item
    html += "</ul>"
    return html


class EditedDataSubmissionView(object):
    def __init__(self, details):
        self.details = details

    def html(self):
        html = []
        html.append("%s: %s" % (ugettext("Submission Received on"), self.details[RECEIVED_ON]))
        if self.details[STATUS_CHANGED]:
            html.append(ugettext('Changed Status: "Error" to "Success"'))

        if CHANGED_ANSWERS in self.details:
            html.append(ugettext('Changed Answers:'))
            unsorted_list = '<ul class="bulleted">'
            for key, value in self.details[CHANGED_ANSWERS].iteritems():
                unsorted_list += self._html_li_tag(key, value)
            html.append(unsorted_list + "</ul>")
        return "<br/>".join(html)

    def _html_li_tag(self, key, value):
        return "<li>%s: %s</li>" % (
            key, '"' + unicode(value[OLD]) + '" ' + ugettext('to') + ' "' + unicode(value[NEW]) + '"')


class EditedRegistrationFormView(object):
    def __init__(self, details):
        self.details = details

    def html(self):
        html = []
        if "entity_type" in self.details:
            html.append("%s: %s" % (ugettext("Subject Type"), self.details["entity_type"]))

        if "form_code" in self.details:
            html.append("%s: %s" % (ugettext("Questionnaire Code"), self.details["form_code"]))

        html.append(get_questionnaire_detail(self.details))
        return "<br/>".join(html)


class EditedProjectView(object):
    def __init__(self, details):
        self.details = details

    def html(self):
        questionnaire_detail = [get_questionnaire_detail(self.details)]
        for type in ["changed", "added", "changed_type", "deleted",
                     "hint_changed", "constraint_message_changed", "constraint_changed", "relevant_changed",
                     "required_changed", "default_changed", "appearance_changed", "choice_changed"]:
            try:
                self.details.pop(type)
            except:
                pass
        html = self._get_detail(self.details)
        html.extend(questionnaire_detail)
        return "<br/>".join(html)


    def _get_detail(self, detail_dict):
        detail_list = []
        for key, changed in detail_dict.items():
            detail_list.append("%s: %s" % (ugettext(key), changed))
        return detail_list