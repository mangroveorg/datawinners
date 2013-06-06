function (doc) {
    if (doc.document_type == 'Project' && !doc.void) {
        emit(doc.qid, doc);
    }
}