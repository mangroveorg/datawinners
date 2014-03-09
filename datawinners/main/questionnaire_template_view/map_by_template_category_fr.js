function (doc) {
    if (doc.language == 'fr') {
        emit(doc.category, {name: doc.name, id: doc._id});
    }
}