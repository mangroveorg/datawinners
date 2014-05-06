function (doc) {
    if (doc.document_type == 'FormModel') {
        if (!doc.void) {
            var unique_id_types = [];
            for (i in doc.json_fields) {
                var field = doc.json_fields[i];
                if (field.type == "unique_id" && unique_id_types.indexOf(field.unique_id_type) == -1) {
                        unique_id_types.push(field.unique_id_type);
                        emit(field.unique_id_type, doc.name);
                }
            }

        }
    }
}
