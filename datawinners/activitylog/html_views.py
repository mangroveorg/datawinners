from django.utils.translation import ugettext

RECEIVED_ON = 'received_on'
STATUS_CHANGED = 'status_changed'
CHANGED_ANSWERS = 'changed_answers'
OLD = 'old'
NEW = 'new'

def get_questionnaire_detail(detail_dict):
    detail_list = []
    for type in ["added", "deleted"]:
        if type in detail_dict:
            str = '<ul class="bulleted">'
            for item in detail_dict[type]:
                str += "<li>%s</li>" % item
            str += "</ul>"
            detail_list.append("%s: %s" % (ugettext("%s Questions" % type.capitalize()), str))

    if "changed" in detail_dict:
        str = '<ul class="bulleted">'
        for changed in detail_dict["changed"]:
            if changed is not None:
                str += "<li>%s</li>" % changed
        str += "</ul>"
        detail_list.append("%s: %s" % (ugettext("Question Labels Changed"), str))

    if "changed_type" in detail_dict:
        response_type = {"select1": "List of Choices", "select": "List of Choices", "text": "Word or Phrase",
                         "integer": "Number", "unique_id": "Identification Number",
                         "geocode": "GPS Coordinates", "date": "date", "telephone_number": "Telephone Number"}
        for type_changed in detail_dict["changed_type"]:
            detail_list.append(ugettext('Answer type changed to %(answer_type)s for \"%(question_label)s\"') %
                               {"answer_type": ugettext(response_type.get(type_changed["type"], "")),
                                "question_label": type_changed["label"]})

    return "<br/>".join(detail_list)


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
        for type in ["changed", "added", "changed_type", "deleted"]:
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