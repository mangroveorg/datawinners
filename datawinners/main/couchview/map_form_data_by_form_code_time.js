function(doc) {
    if (!doc.void && doc.document_type == "DataRecord")
    { 	var c = new Date(doc.created);
        c.setUTCHours(0);
        c.setUTCMinutes(0);
        c.setUTCSeconds(0);
        c.setUTCMilliseconds(0);
        var date = Date.parse(doc.event_time || c);
        var form_code = doc.submission.form_code;
        var data = {};
        for (k in doc.data) {
            value = doc.data[k].value;
            data[k] = value;
        }
        key = [form_code,date];
        emit(key, {'submission_time' : doc.created, 'submission_data' : data});
    }
}