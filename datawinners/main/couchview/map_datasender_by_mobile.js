function(doc) {
    if (doc.document_type == "Entity" && doc.aggregation_paths._type[0] == 'reporter' && !doc.void) {
        var data = doc.data;
        emit([data.mobile_number.value, data.name.value, doc.short_code], null);
    }
}