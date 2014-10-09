function(doc) {
    var isNotNull = function(o) {
        return !((o === undefined) || (o == null));
    };
    if (doc.document_type == 'SurveyResponse' && isNotNull(doc.is_anonymous_submission) && isNotNull(doc.form_model_id)) {
        emit(doc.created_by, doc);
    }
}