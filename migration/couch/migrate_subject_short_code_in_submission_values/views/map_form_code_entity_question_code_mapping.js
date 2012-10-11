function(doc) {
    var entity_field, field;
    if (doc.document_type === 'FormModel' && !doc["void"] && !doc.is_registration_model) {
        entity_field = ((function() {
            var _i, _len, _ref, _results;
            _ref = doc.json_fields;
            _results = [];
            for (_i = 0, _len = _ref.length; _i < _len; _i++) {
                field = _ref[_i];
                if (field["entity_question_flag"] === true) {
                    _results.push(field);
                }
            }
            return _results;
        })())[0];
        emit([doc.form_code, entity_field.code]);
    }
}