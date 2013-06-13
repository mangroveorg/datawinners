from datawinners.main.database import document_stores, test_document_stores

def document_stores_to_process(args):
    if "syncall" in args:
        return document_stores()

    return test_document_stores()
