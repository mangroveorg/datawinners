function(doc) {
    var isNotNull = function(o) {
        return !((o === undefined) || (o == null));
    };
    if (doc.document_type == 'SurveyResponse' && isNotNull(doc.open_datasender_phone_number) && isNotNull(doc.form_code)) {
        emit(doc.open_datasender_phone_number, doc);
    }
}