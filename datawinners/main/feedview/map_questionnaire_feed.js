function (doc) {
    if (doc.document_type == 'EnrichedSurveyResponse') {
        var result = {'id':doc.survey_response_id, 'data_sender_id':doc.data_sender['id'], 'modified':doc.modified}
        var values = {}
        for (key in doc.values) {
            if(doc.values[key].is_entity_question){
                for( answer_key in doc.values[key].answer)
                    values[key] = answer_key
            } else {
                values[key] = doc.values[key].answer
            }
        }
        result['values'] = values
        status = doc.status
        if (doc.void) {
            status = 'deleted'
        }
        result['status'] = status
        emit([doc.form_code, doc.modified], result)
    }
}