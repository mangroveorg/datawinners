function (doc) {
    var documents = [];
    emit(doc.category, {name: doc.name, id: doc._id});
}