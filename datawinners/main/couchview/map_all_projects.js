function(doc) {
    if (doc.document_type == 'FormModel' && !doc.is_registration_model && doc.form_code != 'delete') {
        if(!doc.void){
            emit([doc.created,doc.name], doc);
        }
    }
}
