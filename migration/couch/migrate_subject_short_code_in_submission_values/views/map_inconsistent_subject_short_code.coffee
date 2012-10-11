(doc) ->
  if doc.document_type == "Entity" && !doc.void && doc.aggregation_paths['_type'][0] != "reporter"
    short_code = doc.short_code
    value_of_short_code = (field for label, field of doc.data when (field["value"] + "").toUpperCase() == short_code.toUpperCase())[0]["value"]
    if short_code != value_of_short_code
      emit([value_of_short_code, short_code])