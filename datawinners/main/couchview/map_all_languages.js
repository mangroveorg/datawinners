function (doc) {
    if (doc.document_type == "CustomizedMessage") {
            emit(doc._id, doc.language_name)
    }
}