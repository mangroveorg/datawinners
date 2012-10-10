(doc)->
  if doc.document_type == 'FormModel' && !doc.void && !doc.is_registration_model
    entity_field = (field for field in doc.json_fields when field["entity_question_flag"] == true)[0]
    emit([doc.form_code, entity_field.code])