from datetime import datetime

from pytz import utc


def is_idnr_question(qn):
    return "" in qn.split(".")


def get_indexable_question(qn):
    return is_idnr_question(qn) and qn.split("..")[0] or qn


def get_idnr_question(qn):
    return qn.split("..")[1]


def distinct(values):
    return sorted(set(values), key=lambda x: values.index(x))


def strip_alias(qn):
    return ".".join(qn.split(".")[1:])


def parse_date(date):
    return datetime.strptime(date.strip(), "%d.%m.%Y").replace(tzinfo=utc)
