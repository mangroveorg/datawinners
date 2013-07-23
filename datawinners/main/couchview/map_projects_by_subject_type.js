function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void){
            emit(doc.entity_type, doc.name);
        }
    }
}
