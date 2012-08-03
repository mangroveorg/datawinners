function(doc) {
    if (!doc.void && doc.document_type == "DataRecord")
    {
        var date = Date.parse(doc.event_time);
        var entity = doc.entity;
        var entity_type = entity.aggregation_paths['_type'];
        var entity_id = entity.short_code;
        var data = {};
        for (k in doc.data) {
            value = doc.data[k].value;
            data[k] = value;
        }
        key = [entity_type,entity_id,date];
        emit(key, data);
    }
}