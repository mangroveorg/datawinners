# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

__all__ = ['fetch_', 'from_']


def fetch_(identifier, data_id):
    return data_id[identifier]


def from_(data_id):
    return data_id
