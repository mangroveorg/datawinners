# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
import logging

from django.utils.translation import ugettext
from datawinners.entity.helper import get_country_appended_location
from mangrove.form_model.form_model import get_form_model_by_code
from mangrove.transport.contract.response import Response
from mangrove.transport.player.player import Player
from datawinners.questionnaire.helper import get_location_field_code


class FilePlayer(Player):
    def __init__(self, dbm, parser, channel_name, form_code, location_tree=None):
        Player.__init__(self, dbm, location_tree)
        self.parser = parser
        self.channel_name = channel_name
        self.form_code = form_code
        self.logger = logging.getLogger("websubmission")

    def _appendFailedResponse(self, message, values=None):
        response = Response(reporters=[], survey_response_id=None)
        response.success = False
        response.errors = dict(error=ugettext(message), row=values)
        return response

    def _append_country_for_location_field(self, form_model, values, organization):
        location_field_code = get_location_field_code(form_model)
        if location_field_code is None:
            return values
        if location_field_code in values and values[location_field_code]:
            values[location_field_code] = get_country_appended_location(values[location_field_code],
                                                                        organization.country_name())
        return values

    def _get_form_model(self, rows):
        form_model = None
        if len(rows) > 0:
            (form_code, values) = rows[0]
            form_model = get_form_model_by_code(self.dbm, form_code)
            if self.form_code is not None and form_code != self.form_code:
                form_model = get_form_model_by_code(self.dbm, self.form_code)
                raise FormCodeDoesNotMatchException(
                    ugettext('The file you are uploading is not a list of [%s]. Please check and upload again.') %
                    form_model.entity_type[0], form_code=form_code)
        return form_model

class FormCodeDoesNotMatchException(Exception):
    def __init__(self, message, form_code=None):
        self.message = message
        self.data = form_code

    def __str__(self):
        return self.message

