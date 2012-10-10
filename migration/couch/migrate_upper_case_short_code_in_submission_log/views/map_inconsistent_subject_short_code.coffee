(doc) ->
  if doc.document_type == "Entity" && !doc.void && doc.aggregation_paths['_type'][0] != "reporter"
    short_code = doc.short_code
    value_of_short_code = doc.data['short_code']['value']
    if short_code != value_of_short_code
      emit([short_code, value_of_short_code])