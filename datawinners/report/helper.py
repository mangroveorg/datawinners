def idnr_question(qn):
    return "" in qn.split(".")


def get_indexable_question(qn):
    return idnr_question(qn) and qn.split("..")[:1][0] or qn


def distinct(values):
    return sorted(set(values), key=lambda x: values.index(x))


def strip_alias(qn):
    return ".".join(qn.split(".")[1:])