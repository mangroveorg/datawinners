var doSort = function(data, sortColumns) {
    var obj = prepareSortObject(data, sortColumns);
    var sortedKeys = Object.keys(obj).sort(function(prev, next){ return prev < next ? -1 : prev == next ? 0 : 1 });
    return sortedKeys.reduce(function(acc, key) { return acc.concat(obj[key]); }, []);
};

var prepareSortObject = function(data, sortColumns) {
    var obj = {};
    data.each(function(i, element) {
        var key = sortColumns.reduce(function(acc, colIndex) { return acc + $($(element).find('td')[colIndex]).text() }, "").toLowerCase();
        if (!obj[key]) {
            obj[key] = [];
        }
        obj[key].push(element);
    });
    return obj;
};