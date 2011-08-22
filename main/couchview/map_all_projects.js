function(doc) {
    if (doc.document_type == 'Project') {
        emit(doc.name, doc);
    }
}


