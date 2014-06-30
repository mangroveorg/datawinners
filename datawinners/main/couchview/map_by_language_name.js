function (doc) {
    if (doc.document_type == "CustomizedMessage") {
        emit(doc.language_name.toLowerCase(), doc._id);
    }
}