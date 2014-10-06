function(doc) {
    var isNotNull = function(o) {
        return !((o === undefined) || (o == null));
    };
    if (doc.document_type == 'SurveyResponse' && isNotNull(doc.anonymous_submission) && isNotNull(doc.form_code)) {
        emit(doc.created_by, doc);
    }
}