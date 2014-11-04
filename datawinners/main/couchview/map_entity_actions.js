function(doc) {
    if (doc.document_type == 'EntityAction') {
        emit(Date.parse(doc.created), doc);
    }
}