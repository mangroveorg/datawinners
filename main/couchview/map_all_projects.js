function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void){
            emit([doc.created,doc.name], doc);
        }
    }
}


