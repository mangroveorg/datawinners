from datawinners.entity.entity_exceptions import InvalidFileFormatException
from datawinners.entity.import_datasenders import DataSenderFileUpload
from datawinners.entity.import_subjects import SubjectFileUpload
from datawinners.location.LocationTree import get_location_tree, get_location_hierarchy
from datawinners.submission.location import LocationBridge
from mangrove.transport import Channel
from mangrove.transport.player.parser import CsvParser, XlsParser


class FilePlayerFactory:

    def _create_parser(self, default_parser, extension):
        if default_parser is not None:
            parser = default_parser()
        elif extension == '.csv':
            parser = CsvParser()
        elif extension == '.xls':
            parser = XlsParser()
        else:
            raise InvalidFileFormatException()
        return parser

    def _create_player(self, channel, form_code, manager, parser):
        location_bridge = LocationBridge(get_location_tree(), get_loc_hierarchy=get_location_hierarchy)
        if form_code is None:
            return DataSenderFileUpload(manager, parser, channel, form_code, location_tree=location_bridge)
        else:
            return SubjectFileUpload(manager, parser, channel, form_code, location_tree=location_bridge)

    def create(self, manager, extension, default_parser=None, form_code=None):
        channels = dict({".xls": Channel.XLS, ".csv": Channel.CSV})
        try:
            channel = channels[extension]
        except KeyError:
            raise InvalidFileFormatException()
        parser = self._create_parser(default_parser, extension)
        return self._create_player(channel, form_code, manager, parser)
