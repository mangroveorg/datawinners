function (doc) {
    if (doc.document_type == 'FormModel') {
        if (!doc.void) {
            var unique_id_types = [];
            emit_unique_id_fields_in(doc.json_fields);
        }
    }
    function emit_unique_id_fields_in(fields){
        for (i in fields) {
                    var field = doc.json_fields[i];
                    if (field.type == "unique_id" && unique_id_types.indexOf(field.unique_id_type) == -1) {
                            unique_id_types.push(field.unique_id_type);
                            emit(field.unique_id_type, doc.name);
                    }
            if (field.type == "field_set") {
                            emit_unique_id_fields_in(field.fields)
                    }

                }
        }
}