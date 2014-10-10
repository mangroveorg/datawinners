function(doc) {
    if (doc.document_type == 'SurveyResponse' && typeof doc.is_anonymous_submission !== 'undefined' && doc.is_anonymous_submission) {
        emit(doc.created_by, doc);
    }
}