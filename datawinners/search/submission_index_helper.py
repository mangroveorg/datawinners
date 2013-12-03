from datawinners.search.index_utils import get_elasticsearch_handle


class SubmissionIndexUpdateHandler():
    def __init__(self, index, doc_type):
        self.index = index
        self.doc_type = doc_type

    def update_field_in_submission_index(self, document_id, fields_mapping):
        es = get_elasticsearch_handle()
        es.update(self.index, self.doc_type, id=document_id, doc=fields_mapping)