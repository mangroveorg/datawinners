function(doc) {
    var isNotNull = function(o) {
        return !((o === undefined) || (o == null));
    };
    if (doc.document_type == 'SubmissionLog' && isNotNull(doc.form_code)) {
        emit(doc._id,doc);
    }
}