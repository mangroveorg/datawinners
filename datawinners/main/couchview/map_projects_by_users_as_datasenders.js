function(doc) {
    if (doc.document_type == 'FormModel'&& !doc.is_registration_model) {
        if(!doc.void){
            for(i = 0; i< doc.users_as_datasender.length; i++){
                emit(doc.users_as_datasender[i], null);
	    }
        }
    }
}