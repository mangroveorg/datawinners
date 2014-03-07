function (doc) {
    emit(doc.category, {name: doc.name, id: doc._id});
}