function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void){
            emit(doc.name, doc);
        }
    }
}


