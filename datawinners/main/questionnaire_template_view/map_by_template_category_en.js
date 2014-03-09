function (doc) {
    if (doc.language == 'en') {
        emit(doc.category, {name: doc.name, id: doc._id});
    }
}