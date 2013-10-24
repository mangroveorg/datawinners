//function reload_tables(responseJSON) {
//    $("#imported_table").html('');
//    $("#associated_data_senders tbody").html('');
//    $.each(responseJSON.all_data_senders, function (index, element) {
//        if ($.inArray(element.short_code, responseJSON.associated_datasenders) > 0){
//            var datas = element.cols.join("</td><td>");
//            var html = "<td><input type='checkbox' id='" + element.short_code + "' value='" + element.short_code + "'/></td>";
//            html += "<td>" + element.cols.join("</td><td>");
//            $("#associated_data_senders tbody").append("<tr>" + html + "</tr>");
//            if (element.short_code in responseJSON.imported_entities) {
//                $("#imported_table").append("<tr><td>" + datas + "</td></tr>");
//            }
//        }
//    });
//}

function reload_tables(responseJSON) {
    $("#imported_table").html('');
    $.each(responseJSON.all_data, function (index, element) {
        var datas = element.cols.join("</td><td>");
        if (element.short_code in responseJSON.imported_datasenders) {
            $('#imported_table').append("<tr><td>" + datas + "</td></tr>");
        }
    });
}