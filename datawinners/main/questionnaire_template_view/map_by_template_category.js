function (doc) {
    emit(doc.category, [doc.name, doc._id]);
}