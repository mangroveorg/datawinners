function(doc) {
    if (doc.document_type == 'FormModel') {
         emit(doc.void,1);

    }
}