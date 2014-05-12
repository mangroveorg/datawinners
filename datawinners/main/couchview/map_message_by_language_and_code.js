function (doc) {
    if (doc.document_type == "CustomizedMessage") {
        for (i in doc.messages) {
            emit([doc._id, i], doc.messages[i])
        }
    }
}