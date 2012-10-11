function(doc) {
    var field, label, short_code, value_of_short_code;
    if (doc.document_type === "Entity" && !doc["void"] && doc.aggregation_paths['_type'][0] !== "reporter") {
        short_code = doc.short_code;
        value_of_short_code = ((function() {
            var _ref, _results;
            _ref = doc.data;
            _results = [];
            for (label in _ref) {
                field = _ref[label];
                if ((field["value"] + "").toUpperCase() === short_code.toUpperCase()) {
                    _results.push(field);
                }
            }
            return _results;
        })())[0]["value"];
        if (short_code !== value_of_short_code) {
            emit([value_of_short_code, short_code]);
        }
    }
}