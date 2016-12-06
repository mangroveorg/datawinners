def idnr_question(qn):
    return "" in qn.split(".")


def get_indexable_question(qn):
    return idnr_question(qn) and qn.split("..")[:1][0] or qn
