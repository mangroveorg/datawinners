function(doc) {
    if (doc.document_type == 'ReminderLog') {
        if(!doc.void){
            emit(doc.project_id, null);
        }
    }
}