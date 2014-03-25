function(doc) {
    if (doc.document_type == 'FormModel' && !doc.is_registration_model) {
        if(!doc.void){
            emit(doc.name, doc._id);
        }
    }
}


