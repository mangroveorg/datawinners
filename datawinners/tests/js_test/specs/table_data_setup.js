function ajaxRequestDataValue(data, paramName) {
    var returnVal;
    $(data).each(function () {
        if (this.name == paramName) {
            returnVal = this.value;
            return;
        }
    });
    return returnVal;
}

function setupSpyForTableData() {
    spyOn(jQuery, "ajax").andCallFake(function (params) {
        var iDisplayStart = ajaxRequestDataValue(params.data, 'iDisplayStart') || 0;
        var iDisplayLength = ajaxRequestDataValue(params.data, 'iDisplayLength') || 10;
        var iTotalDisplayRecords = 30;
        var response_text = getResponseText(iTotalDisplayRecords, iDisplayStart, iDisplayLength);

        params.success(response_text);
    });
}


function getResponseText(iTotalDisplayRecords, iDisplayStart, iDisplayLength) {
    var response_text = {"data": [], "iTotalDisplayRecords": iTotalDisplayRecords, "iDisplayStart": iDisplayStart, "iDisplayLength": iDisplayLength};
    var number_of_records = iDisplayLength > iTotalDisplayRecords ? iTotalDisplayRecords : iDisplayLength;
    for (var i = 0; i < number_of_records; i++) {
        response_text.data.push(["Clinic", "ANALAMANGA" + i, "ANALAMANGA,Madagascar", "-18.8, 47.4833", "87654324" + i, "cli" + i])
    }
    return response_text
}
