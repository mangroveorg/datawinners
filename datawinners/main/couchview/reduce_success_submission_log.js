function(keys, values, rereduce) {
    result = {};
    if (rereduce == false) {
        result.count = values.length;
        return result;
    }
    else {
        result.count = 0;
        for (i in values) {
            result.count += values[i].count;
        }
        return result;
    }
}