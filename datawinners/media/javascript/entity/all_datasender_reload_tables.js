function reload_tables(responseJSON) {
    $("#subject_table tbody").html('');
    $.each(responseJSON.all_data, function (index, element) {
        var html = "<td><input type='checkbox' id='" + element.short_code + "' value='" + element.short_code + "'/></td>";
        html += "<td>" + element.cols.join("</td><td>") + "</td><td>" + element.projects + "</td><td>" + element.email + "</td>";
        $("#subject_table tbody").append("<tr>" + html + "</tr>");
    });
}