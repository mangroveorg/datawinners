class DataSender(object):
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

    def __eq__(self, other):
        return isinstance(other,
            DataSender) and self._name == other._name and self._source == other._source and self._reporter_id == other._reporter_id
