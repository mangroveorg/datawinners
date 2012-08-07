function(doc) {
    if (!doc.void && doc.document_type == "DataRecord")
    {
        var date = Date.parse(doc.event_time);
        var form_code = doc.submission.form_code;
        var data = {};
        for (k in doc.data) {
            value = doc.data[k].value;
            data[k] = value;
        }
        key = [form_code,date];
        emit(key, data);
    }
}