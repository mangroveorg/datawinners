from copy import copy
from datawinners.entity.player import FilePlayer
from datawinners.exceptions import InvalidEmailException, NameNotFoundException
from datawinners.utils import get_organization_from_manager
from mangrove.errors.MangroveException import DataObjectAlreadyExists, MangroveException
from mangrove.transport import TransportInfo
from mangrove.transport.work_flow import RegistrationWorkFlow


class SubjectFileUpload(FilePlayer):

    def __init__(self, dbm, parser, channel_name, form_code, location_tree=None):
        FilePlayer.__init__(self, dbm, parser, channel_name, form_code, location_tree)

    def accept(self, file_contents):
        organization = get_organization_from_manager(self.dbm)
        rows = self.parser.parse(file_contents)
        form_model = self._get_form_model(rows)
        responses = []
        for (form_code, values) in rows:
            responses.append(self._import_subject_submission(form_code, organization, values, form_model))
        return responses

    def _import_subject_submission(self, form_code, organization, values, form_model=None):
        self._append_country_for_location_field(form_model, values, organization)
        transport_info = TransportInfo(transport=self.channel_name, source=self.channel_name, destination="")
        submission = self._create_submission(transport_info, form_code, copy(values))
        try:
            values = RegistrationWorkFlow(self.dbm, form_model, self.location_tree).process(values)
            log_entry = "message: " + str(values) + "|source: web|"
            response = self.submit(form_model, values, submission, [])

            if not response.success:
                response.errors = dict(error=response.errors, row=values)
                log_entry += "Status: False"
            else:
                log_entry += "Status: True"
            self.logger.info(log_entry)
            return response
        except DataObjectAlreadyExists as e:
            if self.logger is not None:
                log_entry += "Status: False"
                self.logger.info(log_entry)
            return self._appendFailedResponse("%s with %s = %s already exists." % (e.data[2], e.data[0], e.data[1]),
                                                values=values)
        except (InvalidEmailException, MangroveException, NameNotFoundException) as e:
            return self._appendFailedResponse(e.message, values=values)