function(doc) {
    if (doc.document_type == 'Project') {
        if(!doc.void){
            for(i = 0; i< doc.data_senders.length; i++){
                emit(doc.data_senders[i], null);
	    }
        }
    }
}
