function(doc) {
    if (doc.document_type == 'FormModel'&& !doc.is_registration_model) {
        if(!doc.void){
            for(i = 0; i< doc.users.length; i++){
                emit(doc.users[i], null);
	    }
        }
    }
}