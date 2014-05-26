function (doc) {
    if (doc.document_type == "CustomizedMessage") {
        emit(doc.language_name, doc._id);
    }
}