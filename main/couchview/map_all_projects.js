function(doc) {
  if (doc.document_type == 'Project') {
     emit(null, doc);
  }
}


