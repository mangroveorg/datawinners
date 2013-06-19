class DataSender(object):

    @staticmethod
    def from_tuple(data_sender_tuple):
        return DataSender(data_sender_tuple[-1], data_sender_tuple[0], data_sender_tuple[1])


    def __init__(self, source, name, reporter_id):
        self._source = source
        self._name = name
        self._reporter_id = reporter_id or '-'

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source

    @property
    def reporter_id(self):
        return self._reporter_id


    def __eq__(self, other):
        instance_equal = isinstance(other, DataSender)
        if not instance_equal: return False

        if isinstance(self.source, list):
            source_equal = set(self.source) == set(other._source)
        else:
            source_equal = self.source == other._source

        return self._name == other._name and source_equal and self._reporter_id == other._reporter_id

    def __hash__(self):
        result = 17
        result = 31 * result + hash(self._name)
        result = 31 * result + hash(self._source)
        result = 31 * result + hash(self._reporter_id)

        return result


