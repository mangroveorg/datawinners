from django.utils.translation import ugettext

RECEIVED_ON = 'received_on'
STATUS_CHANGED = 'status_changed'
CHANGED_ANSWERS = 'changed_answers'
OLD = 'old'
NEW = 'new'

class EditedDataSubmissionView(object):
    def __init__(self, details):
        self.details = details

    def html(self):
        html = []
        html.append("%s: %s" % (ugettext("Submission Received on"), self.details[RECEIVED_ON]))
        if self.details[STATUS_CHANGED]:
            html.append(ugettext('Changed Status: "Error" to "Success"'))
        if self.details[CHANGED_ANSWERS]:
            html.append(ugettext('Changed Answers:'))
            unsorted_list = '<ul class="bulleted">'
            for key, value in self.details[CHANGED_ANSWERS].iteritems():
                unsorted_list += self._html_li_tag(key, value)
            html.append(unsorted_list + "</ul>")
        return html

    def _html_li_tag(self, key, value):
        return "<li>%s: %s</li>" % (key, '"' + str(value[OLD]) + '" ' + ugettext('to') + ' "' + str(value[NEW]) + '"')
