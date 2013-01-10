class DataSender(object):

    @staticmethod
    def from_tuple(data_sender_tuple):
        return DataSender(data_sender_tuple[-1], data_sender_tuple[0], data_sender_tuple[1])


    def __init__(self, source, name, reporter_id):
        self._source = source
        self._name = name
        self._reporter_id = reporter_id

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source

    @property
    def reporter_id(self):
        return self._reporter_id

    def to_tuple(self):
        if self._name == 'TEST':
            return "TEST", "", "TEST"

        return self._name, self._reporter_id, ','.join(self._source)

    def __eq__(self, other):
        return isinstance(other,
            DataSender) and self._name == other._name and self._source == other._source and self._reporter_id == other._reporter_id

    def __hash__(self):
        result = 17
        result = 31 * result + hash(self._name)
        result = 31 * result + hash(self._source)
        result = 31 * result + hash(self._reporter_id)

        return result


