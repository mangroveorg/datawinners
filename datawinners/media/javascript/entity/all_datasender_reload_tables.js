function reload_tables(responseJSON) {
    $("#imported_table").html('');
    $.each(responseJSON.all_data, function (index, element) {
        var datas = element.cols.join("</td><td>");
        if (element.short_code in responseJSON.imported_datasenders) {
            $('#imported_table').append("<tr><td>" + datas + "</td></tr>");
        }
    });
}
