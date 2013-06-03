function (doc) {
    if (doc.document_type == 'EnrichedSurveyResponse') {
        emit(doc.survey_response_id, doc)
    }
}