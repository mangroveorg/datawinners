function (doc) {
    if (doc.document_type == 'FormModel') {
        if (!doc.void) {
            for (i in doc.json_fields) {
                var field = doc.json_fields[i];
                if (field.type == "unique_id") {
                    emit(field.unique_id_type, doc.name);
                }
            }

        }
    }
}
